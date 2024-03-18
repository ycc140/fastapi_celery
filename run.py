#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2024-03-18 22:09:25
     $Rev: 1
"""

# BUILTIN modules
import json

# Third party modules
import uvicorn

# Local modules
from src.main import app
from src.config.setup import config

if __name__ == "__main__":
    uv_config = {'ssl_keyfile': "certs/private-key.pem",
                 'ssl_certfile': "certs/public-cert.pem",
                 'log_config': {"disable_existing_loggers": False, "version": 1},
                 'app': 'src.main:app', 'log_level': config.log_level, 'reload': True}

    # So you can se test the handling of different log levels.
    app.logger.debug(f'{config.name} v{config.version} has initiated...')

    # Log config values for testing purposes.
    app.logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')

    uvicorn.run(**uv_config)
