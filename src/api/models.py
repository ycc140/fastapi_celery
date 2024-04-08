# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2024-04-08 17:11:52
     $Rev: 7
"""

# BUILTIN modules
from uuid import UUID
from typing import Optional, List, Union

# Third party modules
from pydantic import ConfigDict, BaseModel

# local modules
from .documentation import (process_example, status_example,
                            retry_example, health_example)


# -----------------------------------------------------------------------------
#
class BadStateError(BaseModel):
    """ Define OpenAPI documentation for a http 400 exception (Bad Request).

    :ivar detail: Error detail text.
    """
    detail: str = "Task ID has the wrong state for a retry (not FAILED)"


class NotFoundError(BaseModel):
    """ Define OpenAPI documentation for a http 404 exception (Not Found).

    :ivar detail: Error detail text.
    """
    detail: str = "Task ID not found"


class HealthStatusError(BaseModel):
    """ Define OpenAPI documentation for a http 500 exception (INTERNAL_SERVER_ERROR).

    :ivar detail: Error detail text.
    """
    detail: str = "HEALTH: resource connection(s) are down"


class UnknownError(BaseModel):
    """ Define OpenAPI documentation for a http 500 exception (INTERNAL_SERVER_ERROR).

    :ivar detail: Error detail text.
    """
    detail: str = "Celery task initialization failed"


# -----------------------------------------------------------------------------
#
class ResourceModel(BaseModel):
    """ Representation of a health resources response.

    :ivar name: Resource name.
    :ivar status: Resource status
    """
    name: str
    status: bool


# -----------------------------------------------------------------------------
#
class HealthResponseModel(BaseModel):
    """ Define the OpenAPI model for the health response.

    :ivar name: Service name.
    :ivar status: Overall health status
    :ivar version: Service version.
    :ivar resources: Status for individual resources.
    :ivar cert_remaining_days: Remaining SSL/TLS certificate valid days.
    """
    model_config = ConfigDict(json_schema_extra={"example": health_example})

    name: str
    status: bool
    version: str
    cert_remaining_days: int
    resources: List[ResourceModel]


# -----------------------------------------------------------------------------
#
class ProcessResponseModel(BaseModel):
    """ Define the OpenAPI model for API process_payload responses.

    :ivar id: Task ID for the current job.
    :ivar status: Response status (REVOKED|STARTED|PENDING|RETRY|FAILURE|SUCCESS).
    """
    model_config = ConfigDict(json_schema_extra={"example": process_example})

    id: UUID
    status: str


# -----------------------------------------------------------------------------
#
class StatusResponseModel(BaseModel):
    """ Define the OpenAPI model for a pending API check_task_status responses.

    :ivar status: Response status (REVOKED|STARTED|PENDING|RETRY|FAILURE|SUCCESS).
    :ivar result: Possible response message when status is FAILURE or SUCCESS.
    """
    model_config = ConfigDict(json_schema_extra={"example": status_example})

    status: str
    result: Optional[Union[dict, str]] = None


# -----------------------------------------------------------------------------
#
class RetryResponseModel(BaseModel):
    """ Define the OpenAPI model for API retry_failed_task responses.

    :ivar status: Response status (REVOKED|STARTED|PENDING|RETRY|FAILURE|SUCCESS).
    :ivar task_id: Task ID for the current job.
    :ivar failed_id: Task ID for a failed job.
    """
    model_config = ConfigDict(json_schema_extra={"example": retry_example})

    status: str
    task_id: UUID
    failed_id: UUID
