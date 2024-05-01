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
from loguru import logger
from httpx import AsyncClient

# Local program modules
from ..src.main import app

# Remove all loggers (not needed during testing).
logger.remove()


# ---------------------------------------------------------
#
@pytest.fixture(scope="module")
def anyio_backend():
    """ Module fixture. """

    return 'asyncio'


# ---------------------------------------------------------
#
@pytest.fixture(scope="module")
async def test_app():
    """ Module fixture. """

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
