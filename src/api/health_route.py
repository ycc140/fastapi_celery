# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2023-08-27 15:46:50
     $Rev: 48
"""

# Third party modules
from fastapi import APIRouter
from fastapi.responses import JSONResponse

# local modules
from .models import HealthResponseModel, HealthStatusError
from ..tools.health_manager import get_health_status

# Constants
ROUTER = APIRouter(prefix="/health", tags=["Health endpoint"])
""" Health API endpoint router. """


# ---------------------------------------------------------
#
@ROUTER.get(
    '',
    response_model=HealthResponseModel,
    responses={500: {"model": HealthStatusError}},
)
async def health_check() -> HealthResponseModel:
    """ **Return connection status for Celery workers.** """

    content = await get_health_status()
    response_code = (200 if content.status else 500)

    return JSONResponse(status_code=response_code,
                        content=content.model_dump())
