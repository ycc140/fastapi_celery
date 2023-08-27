# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2023-08-27 14:44:51
     $Rev: 47
"""

# BUILTIN modules
from typing import Optional, List, Union

# Third party modules
from pydantic import ConfigDict, UUID4, BaseModel

# local modules
from .documentation import (process_example, status_example,
                            retry_example, resource_example)


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
    """ Representation of a health response.

    :ivar name: Service name.
    :ivar status: Overall health status
    :ivar version: Service version.
    :ivar resources: Status for individual resources.
    """

    name: str
    status: bool
    version: str
    resources: List[ResourceModel]
    model_config = ConfigDict(json_schema_extra={"example": resource_example})


# -----------------------------------------------------------------------------
#
class ProcessResponseModel(BaseModel):
    """ Define Swagger model for API process_payload responses.

    :ivar id: Task ID for current job.
    :ivar status: Response status (REVOKED|STARTED|PENDING|RETRY|FAILURE|SUCCESS).
    """

    id: UUID4
    status: str
    model_config = ConfigDict(json_schema_extra={"example": process_example})


# -----------------------------------------------------------------------------
#
class StatusResponseModel(BaseModel):
    """ Define Swagger model for a pending API check_task_status responses.

    :ivar status: Response status (REVOKED|STARTED|PENDING|RETRY|FAILURE|SUCCESS).
    :ivar result: Possible response message when status is FAILURE or SUCCESS.
    """

    status: str
    result: Optional[Union[dict, str]] = None
    model_config = ConfigDict(json_schema_extra={"example": status_example})


# -----------------------------------------------------------------------------
#
class RetryResponseModel(BaseModel):
    """ Define Swagger model for API retry_failed_task responses.

    :ivar status: Response status (REVOKED|STARTED|PENDING|RETRY|FAILURE|SUCCESS).
    :ivar task_id: Task ID for current job.
    :ivar failed_id: Task ID for failed job.
    """

    status: str
    task_id: UUID4
    failed_id: UUID4
    model_config = ConfigDict(json_schema_extra={"example": retry_example})
