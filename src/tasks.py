# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2023-07-17 00:27:46
     $Rev: 26
"""

# BUILTIN modules
import time
import random
import asyncio

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
async def _send_callback_response(task_id: str, url: str,
                                  status: str, payload: dict):
    """ Send processing result to calling service using a RESTful API URL call.

    :param task_id: Current task ID.
    :param url: External service callback URL.
    :param status: Processing status.
    :param payload: processing result.
    """

    try:
        result = {'job_id': task_id, 'status': status, 'result': payload}

        async with AsyncClient() as client:
            resp = await client.post(url=url, json=result,
                                     auth=(config.service_user, config.service_pwd),
                                     timeout=config.url_timeout, headers=config.hdr_data)

        if resp.status_code == 202:
            logger.success(f"Sent POST callback to URL {url} - "
                           f"[{resp.status_code}: {resp.json()}].")

        else:
            logger.error(f"Failed POST callback to URL {url} - "
                         f"[{resp.status_code}: {resp.json()}].")

    except (ConnectError, ConnectTimeout):
        logger.error(f"No connection with URL callback: {url}")


# ---------------------------------------------------------
#
async def _send_rabbit_response(task_id: str, queue: str,
                                status: str, payload: dict):
    """ Send processing result to calling service RabbitMQ queue.

    :param task_id: Current task ID.
    :param queue: External service response queue.
    :param status: Processing status.
    :param payload: processing result.
    """

    try:
        result = {'job_id': task_id, 'status': status, 'result': payload}

        client = RabbitClient(config.rabbit_url)
        await client.send_message(result, queue)

        logger.success(f"Sent RabbitMQ response to queue {queue}.")

    except BaseException as why:
        logger.error(f"No connection with RabbitMQ for queue {queue}: {why}")


# ---------------------------------------------------------
#
def _do_the_work(payload: dict) -> dict:
    """ Do the real work here.

    :param payload: processing result.
    :return: Processing result.
    """

    logger.debug(f'Processing received payload: {payload}')

    # Mimic random error for testing purposes.
    if not random.choice([0, 1]):
        raise ValueError('Oops, something went wrong')

    # Simulate a lengthy processing task.
    time.sleep(15)

    # Return the processing result of the lengthy task.
    return {'message': 'Lots of work was done here'}


# ---------------------------------------------------------
#
@WORKER.task(name='processor', bind=True,
             default_retry_delay=10, max_retries=2)
def processor(task: callable, payload: dict) -> dict:
    """ Let's simulate a long-running task here.

    Using the random module to generate errors now and
    then to be able to test the retry functionality.

    A caller callback URL is used when the callback parameter is part
    of the payload. This means that the callback is called with the
    processing result, good or bad.

    :param task: Current task (Used for retries).
    :param payload: Process received message.
    :return: Processing response.
    """

    try:
        result = _do_the_work(payload)

        if 'callback' in payload:
            asyncio.run(_send_callback_response(task.request.id,
                                                payload['callback'],
                                                'SUCCESS', result))

        if 'responseQueue' in payload:
            asyncio.run(_send_rabbit_response(task.request.id,
                                              payload['responseQueue'],
                                              'SUCCESS', result))

        return result

    except BaseException as why:
        logger.warning('exception raised, processing is '
                       'retried (max 2 times) after 10 seconds')

        # All the retries have failed, so report
        # FAILURE and trigger final exception.
        if task.request.retries == task.max_retries:
            logger.error('Retry processing failed')
            result = {'message': str(why)}

            if 'callback' in payload:
                asyncio.run(_send_callback_response(task.request.id,
                                                    payload['callback'],
                                                    'FAILURE', result))

            if 'responseQueue' in payload:
                asyncio.run(_send_rabbit_response(task.request.id,
                                                  payload['responseQueue'],
                                                  'FAILURE', result))

            raise

        processor.retry(exc=why)
