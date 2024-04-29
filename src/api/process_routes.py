# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2024-04-29 17:18:03
     $Rev: 10
"""

# BUILTIN modules
from uuid import UUID

# Third party modules
from loguru import logger
from celery.result import AsyncResult
from kombu.exceptions import OperationalError
from fastapi import HTTPException, Depends, APIRouter, Query

# local modules
from ..tasks import processor, WORKER
from .documentation import post_query_documentation as query_doc
from ..tools.security import validate_authentication
from .models import (ArgumentError, ProcessResponseModel,
                     StatusResponseModel, RetryResponseModel,
                     NotFoundError, UnknownError, BadStateError)

# Constants
ROUTER = APIRouter(prefix="/v1/process", tags=["Process endpoints"],
                   dependencies=[Depends(validate_authentication)])
""" Process API endpoint router. """


# ---------------------------------------------------------
#
@ROUTER.post(
    '', status_code=202,
    response_model=ProcessResponseModel,
    responses={500: {"model": UnknownError},
               406: {"model": ArgumentError}}
)
async def process_payload(
        payload: dict,
        callback_url: str = Query(**query_doc['callback_url']),
        callback_queue: str = Query(**query_doc['callback_queue']),
) -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**

    :param payload: Data to be processed by Celery.
    :param callback_url: Optional URL callback query parameter.
    :param callback_queue: Optional queue callback query parameter.
    """

    # Verify that none, or only one of the query parameters has a value.
    if all(info is not None for info in (callback_queue, callback_url)):
        errmsg = "Only one query argument can be provided in query URL"
        raise HTTPException(status_code=406, detail=errmsg)

    # Send payload and query arguments to Celery for processing.
    try:
        params = {'callbackUrl': callback_url, 'callbackQueue': callback_queue}
        result = processor.delay(payload, params)
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)


# ---------------------------------------------------------
#
@ROUTER.post(
    '/retry/{failed_id}', status_code=202,
    response_model=RetryResponseModel,
    responses={400: {"model": BadStateError},
               404: {"model": NotFoundError}}
)
async def retry_failed_task(failed_id: UUID) -> RetryResponseModel:
    """**Trigger a retry for a previously failed task.**

    :param failed_id: Failed task ID that should be re-tried.
    """

    # Extract and return Celery processing status from DB.
    if meta := WORKER.backend.get_task_meta(str(failed_id)):

        if meta['status'] == 'FAILURE':
            task = WORKER.tasks[meta['name']]
            result = task.apply_async(args=meta['args'])
            return RetryResponseModel(task_id=result.id,
                                      failed_id=failed_id,
                                      status=result.state)

        errmsg = (f"Task ID {failed_id} has the "
                  f"wrong state for a retry (not FAILED)")
        raise HTTPException(status_code=400, detail=errmsg)

    raise HTTPException(status_code=404,
                        detail=f"Task ID {failed_id} does not exist")


# ---------------------------------------------------------
#
@ROUTER.get(
    '/status/{task_id}',
    response_model_exclude_unset=True,
    response_model=StatusResponseModel,
    responses={404: {"model": NotFoundError}}
)
async def check_task_status(task_id: UUID) -> StatusResponseModel:
    """**Return specified Celery task progress status.**

    :param task_id: Task ID to check status for.
    """

    # Extract and return Celery processing status from DB.
    if not WORKER.backend.get_task_meta(str(task_id)):
        raise HTTPException(status_code=404,
                            detail=f"Task ID {task_id} does not exist")

    # Check Celery task processing status.
    status = AsyncResult(str(task_id))

    # Task processing has not finished yet.
    if not status.ready():
        return StatusResponseModel(status=status.state)

    # Extract and return Celery processing status from DB.
    if result := WORKER.backend.get_task_meta(str(task_id)):
        key = ('result' if result['status'] == 'SUCCESS' else 'traceback')
        return StatusResponseModel(status=result['status'], result=result[key])
