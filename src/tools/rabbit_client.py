# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_celery
  $Author: Anders Wiklund
    $Date: 2023-07-18 09:44:19
     $Rev: 32
"""

# BUILTIN modules
import json
import asyncio
from typing import Callable, Optional

# Third party modules
from aio_pika import connect, connect_robust, Message, DeliveryMode
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection


# -----------------------------------------------------------------------------
#
class RabbitClient:
    """ This class implements RabbitMQ Publish and Subscribe async handling.

    The RabbitMQ queue mechanism is used so that we can take advantage of
    good horizontal message scaling when needed.
    """

    # ---------------------------------------------------------
    #
    def __init__(self, rabbit_url: str, service: Optional[str] = None,
                 incoming_message_handler: Optional[Callable] = None):
        """ The class initializer.

        :param rabbit_url: RabbitMQ's connection URL.
        :param service: Name of message subscription queue.
        :param incoming_message_handler: Received message callback method.
        """

        # Unique parameters.
        self.rabbit_url = rabbit_url
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
    async def start_subscription(self) -> AbstractRobustConnection:
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

        # Start consuming existing and future messages.
        await queue.consume(self._process_incoming_message, no_ack=False)

        return connection

    # ---------------------------------------------------------
    #
    async def publish_message(self, queue: str, message: dict):
        """ Publish message on specified RabbitMQ queue asynchronously.

        :param queue: Publishing queue.
        :param message: Message to be published.
        """
        connection = await connect(url=self.rabbit_url)
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
