# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2023-09-06 14:13:38
     $Rev: 50
"""

# BUILTIN modules
from typing import Annotated

# Third party modules
from loguru import logger
from pydantic import UUID4
from celery.result import AsyncResult
from kombu.exceptions import OperationalError
from fastapi import HTTPException, Depends, APIRouter, Body

# local modules
from ..tasks import processor, WORKER
from ..tools.security import validate_authentication
from .documentation import process_request_body_example
from .models import (NotFoundError, UnknownError, BadStateError,
                     ProcessResponseModel, StatusResponseModel,
                     RetryResponseModel)

# Constants
ROUTER = APIRouter(prefix="/v1/process", tags=["Process endpoints"])
""" Process API endpoint router. """


# ---------------------------------------------------------
#
@ROUTER.post('', status_code=202,
             response_model=ProcessResponseModel,
             responses={500: {"model": UnknownError}},
             dependencies=[Depends(validate_authentication)])
async def process_payload(payload: Annotated[
    dict,
    Body(openapi_examples=process_request_body_example)
]) -> ProcessResponseModel:
    """**Trigger Celery task processing of specified payload.**"""

    try:
        # Add payload message to Celery for processing.
        result = processor.delay(payload)
        logger.debug(f'Added task [{result.id}] to Celery for processing')
        return ProcessResponseModel(status=result.state, id=result.id)

    except OperationalError as why:
        errmsg = f'Celery task initialization failed: {why}'
        logger.error(errmsg)
        raise HTTPException(status_code=500, detail=errmsg)


# ---------------------------------------------------------
#
@ROUTER.post('/retry/{failed_id}', status_code=202,
             response_model=RetryResponseModel,
             responses={400: {"model": BadStateError},
                        404: {"model": NotFoundError}},
             dependencies=[Depends(validate_authentication)])
async def retry_failed_task(failed_id: UUID4) -> RetryResponseModel:
    """**Trigger a retry for a previously failed task.**"""

    # Extract and return Celery processing status from DB.
    if meta := WORKER.backend.get_task_meta(str(failed_id)):

        if meta['status'] == 'FAILURE':
            task = WORKER.tasks[meta['name']]
            result = task.apply_async(args=meta['args'])
            return RetryResponseModel(task_id=result.id,
                                      failed_id=failed_id,
                                      status=result.state)

        errmsg = f"Task ID {failed_id} has the " \
                 f"wrong state for a retry (not FAILED)"
        raise HTTPException(status_code=400, detail=errmsg)

    raise HTTPException(status_code=404,
                        detail=f"Task ID {failed_id} does not exist")


# ---------------------------------------------------------
#
@ROUTER.get('/status/{task_id}',
            response_model_exclude_unset=True,
            response_model=StatusResponseModel,
            responses={404: {"model": NotFoundError}},
            dependencies=[Depends(validate_authentication)])
async def check_task_status(task_id: UUID4) -> StatusResponseModel:
    """**Return specified Celery task progress status.**"""

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
