# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2024-03-18 22:09:25
     $Rev: 1
"""

# BUILTIN modules
import json
import time
import random
import asyncio
from typing import Any
from traceback import format_exception

# Third party modules
from celery import Celery
from celery.utils.log import get_task_logger
from httpx import AsyncClient, ConnectTimeout, ConnectError

# Local modules
from .config.setup import config
from .config import celery_config
from .tools.rabbit_client import RabbitClient
from .tools.custom_logging import create_unified_logger

# Constants
WORKER = Celery(__name__)
""" Celery worker instance. """

# ---------------------------------------------------------

# Read Celery config values.
WORKER.config_from_object(celery_config)

# Create unified Celery task logger instance.
get_task_logger(__name__)
logger = create_unified_logger()


# ---------------------------------------------------------
#
async def send_restful_response(url: str, result: dict):
    """ Send a processing result to calling service using a RESTful URL call.

    :param url: External service callback URL.
    :param result: Processing result.
    """

    try:
        async with AsyncClient() as client:
            resp = await client.post(url=url, timeout=config.url_timeout,
                                     json=result, headers=config.hdr_data)

        if resp.status_code == 202:
            logger.success(f"Sent POST response to URL {url} - "
                           f"[{resp.status_code}: {resp.json()}].")

        else:
            logger.error(f"Failed POST response to URL {url} - "
                         f"[{resp.status_code}: {resp.json()}].")

    except (ConnectError, ConnectTimeout):
        logger.error(f"No connection with response URL: {url}")


# ---------------------------------------------------------
#
async def send_rabbit_response(queue_name: str, result: dict):
    """ Send processing result to calling service using a RabbitMQ queue.

    :param queue_name: External service response queue name.
    :param result: processing result.
    """

    try:
        client = RabbitClient(config.rabbit_url)
        await client.publish_message(queue_name, result)
        logger.success(f"Sent response to RabbitMQ queue {queue_name}.")

    except Exception as why:
        logger.error(f"No connection with RabbitMQ queue {queue_name}: {why}")


# ---------------------------------------------------------
#
def response_handler(task: callable, status: str, retval: Any,
                     task_id: str, args: list, _, __):
    """
    Return the processing response, good or bad when the task is finished
    when the caller has requested it.

    When the 'responseUrl' parameter is one of the input arguments, the
    processing result is returned to the caller by using a RESTful
    POST call to the specified callback URL.

    When the 'responseQueue' parameter is one of the input arguments,
    the processing result is returned to the caller by publishing it
    on the specified RabbitMQ queue.

    :param task: Current task.
    :param status: Current task state.
    :param retval: Task return value/exception.
    :param task_id: Unique id of the task.
    :param args: Original arguments for the task.
    :param _: Not used (needed for correct signature).
    :param __: Not used (needed for correct signature).
    """
    payload = args[0]

    # Check if any more work needs to be done here.
    if not payload.get('responseUrl', payload.get('responseQueue')):
        return

    if status == 'SUCCESS':
        result = retval

    else:
        logger.error(f"Task '{task.name}' retry processing failed")
        result = {'message': format_exception(retval)}

    response = {'job_id': task_id, 'status': status, 'result': result}

    if 'responseUrl' in payload:
        asyncio.run(send_restful_response(payload['responseUrl'], response))

    if 'responseQueue' in payload:
        asyncio.run(send_rabbit_response(payload['responseQueue'], response))


# ---------------------------------------------------------
#
@WORKER.task(
    name='tasks.processor',
    after_return=response_handler,
    autoretry_for=(BaseException,),
    bind=True, default_retry_delay=10, max_retries=2
)
def processor(task: callable, payload: dict) -> dict:
    """ Let's simulate a long-running task here.

    Using the random module to generate errors now and
    then to be able to test the retry functionality.

    :param task: Current task.
    :param payload: Process the received payload.
    :return: Processing response.
    """

    logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
    logger.debug(f"Task '{task.name}' is processing received payload: {payload}")

    # Mimic random error for testing purposes.
    if not random.choice([0, 1]):
        raise ValueError('Oops, something went wrong')

    # Simulate a lengthy processing task.
    time.sleep(15)

    # Return the processing result of the lengthy task.
    return {'message': 'Lots of work was done here'}
