#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2023-07-18 01:40:52
     $Rev: 31
"""

# BUILTIN modules
import asyncio
import contextlib

# Local modules
from src.tools.rabbit_client import RabbitConsumer

# Constants
SERVICE = 'CallerService'


# ---------------------------------------------------------
#
async def process_incoming_message(message: dict):
    """ Print received message.

    :param message:
    """
    print(f'Received: {message}')


# ---------------------------------------------------------
#
async def receiver():
    """ Start a asyncio task to consume messages. """
    print(f'Started RabbitMQ message queue subscription on {SERVICE}...')
    client = RabbitConsumer(SERVICE, process_incoming_message)
    connection = await asyncio.create_task(client.consume())

    try:
        # Wait until terminate
        await asyncio.Future()

    finally:
        await connection.close()


# ---------------------------------------------------------

if __name__ == "__main__":

    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(receiver())
