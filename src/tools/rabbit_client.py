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
import json
import asyncio
from typing import Callable

# Third party modules
from aio_pika import connect, connect_robust, Message, DeliveryMode
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection

# Local modules
from ..config.setup import config


# ---------------------------------------------------------
#
async def publish_rabbit_message(message: dict, queue: str):
    """ Publish message on specified RabbitMQ queue asynchronously.

    :param message: Message to be sent.
    :param queue: Message queue to use for message sending.
    """
    connection = await connect(config.rabbit_url)
    channel = await connection.channel()

    # Create message and publish it.
    message_body = Message(
        content_type='application/json',
        delivery_mode=DeliveryMode.PERSISTENT,
        body=json.dumps(message, ensure_ascii=False).encode())
    await channel.default_exchange.publish(
        routing_key=queue, message=message_body)

    # Close the connection properly.
    await connection.close()


# -----------------------------------------------------------------------------
#
class RabbitConsumer:
    """ This class handles asynchronous RabbitMQ queue subscriptions.

    Note: the queue mechanism is implemented to take advantage of good
    horizontal message scaling when needed.
    """

    rabbit_url = config.rabbit_url

    # ---------------------------------------------------------
    #
    def __init__(self, service: str = None,
                 incoming_message_handler: Callable = None):
        """ The class initializer.

        :param service: Name of receiving service.
        :param incoming_message_handler: Incoming message callback method.
        """

        # Unique parameters.
        self.service_name = service
        self.message_handler = incoming_message_handler

    # ---------------------------------------------------------
    #
    async def _process_incoming_message(self, message: AbstractIncomingMessage):
        """ Processing incoming message from RabbitMQ.

        :param message: Received message.
        """
        if body := message.body:
            await self.message_handler(json.loads(body))

        await message.ack()

    # ---------------------------------------------------------
    #
    async def consume(self) -> AbstractRobustConnection:
        """ Setup message listener with the current running asyncio loop. """
        loop = asyncio.get_running_loop()

        # Perform receive connection.
        connection = await connect_robust(loop=loop, url=self.rabbit_url)

        # Creating receive channel and setting quality of service.
        channel = await connection.channel()

        # To make sure the load is evenly distributed between the workers.
        await channel.set_qos(1)

        # Creating a receive queue.
        queue = await channel.declare_queue(name=self.service_name, durable=True)

        # Start consumption of existing and future messages.
        await queue.consume(self._process_incoming_message, no_ack=False)

        return connection
