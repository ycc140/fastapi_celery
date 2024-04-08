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

# Third party modules
import pytest
from loguru import logger
from starlette.testclient import TestClient

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
def test_app():
    """ Module fixture. """

    with TestClient(app=app) as test_client:
        yield test_client
