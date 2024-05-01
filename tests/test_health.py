# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2024-05-01 15:39:55
     $Rev: 11
"""

# Third party modules
import pytest
from httpx import AsyncClient


# ---------------------------------------------------------
#
@pytest.mark.anyio
async def test_health(test_app: AsyncClient):
    """ Test successful or failed health endpoint.

    :param test_app: TestClient instance.
    """
    response = await test_app.get("/health")

    # The Celery worker is started.
    if response.json()['status'] is True:
        assert response.status_code == 200

    else:
        assert response.status_code == 500
        assert response.json()['status'] is False
