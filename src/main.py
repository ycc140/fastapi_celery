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

# BUILTIN modules
import json
from typing import Any
from pathlib import Path

# Third party modules
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# local modules
from .config.setup import config
from .api import process_routes, health_route
from .tools.custom_logging import create_unified_logger
from .api.documentation import (license_info, tags_metadata, description)


# -----------------------------------------------------------------------------
#
class Service(FastAPI):
    """
    This class adds router and image handling for the OpenAPI documentation
    as well as unified logging.


    @type logger: C{loguru.logger}
    @ivar logger: logger object instance.
    """

    # ---------------------------------------------------------
    #
    def __init__(self, *args: Any, **kwargs: Any):
        """ The class constructor.

        :param args: named arguments.
        :param kwargs: key-value pair arguments.
        """

        super().__init__(*args, **kwargs)

        # Needed for OpenAPI Markdown images to be displayed.
        static_path = Path(__file__).parent / 'design'
        self.mount("/static", StaticFiles(directory=static_path))

        # Add declared router information (note that
        # the order is related to the documentation order).
        self.include_router(process_routes.ROUTER)
        self.include_router(health_route.ROUTER)

        # Unify logging within the imported package's closure.
        self.logger = create_unified_logger()


# ---------------------------------------------------------

# Instantiate the service.
app = Service(
    redoc_url=None,
    title=config.name,
    version=config.version,
    description=description,
    license_info=license_info,
    openapi_tags=tags_metadata,
)

# Test log level and show Log config values for testing purposes.
if Path('/.dockerenv').exists():
    app.logger.debug(f'{config.name} v{config.version} has initiated...')
    app.logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')
