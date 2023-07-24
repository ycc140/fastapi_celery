#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2023-07-24 11:01:45
     $Rev: 40
"""

# BUILTIN modules
import json

# Third party modules
import uvicorn

# Local modules
from src.main import app
from src.config.setup import config


if __name__ == "__main__":

    uv_config = {'ssl_keyfile': "certs/251024-key.pem",
                 'ssl_certfile': "certs/251024-cert.pem",
                 'log_config': {"disable_existing_loggers": False, "version": 1},
                 'app': 'src.main:app', 'log_level': config.log_level, 'reload': True}

    # So you can se test the handling of different log levels.
    app.logger.debug(f'{config.name} v{config.version} has initiated...')

    # Log config values for testing purposes.
    app.logger.trace(f'config: {json.dumps(config.model_dump(), indent=2)}')

    uvicorn.run(**uv_config)
