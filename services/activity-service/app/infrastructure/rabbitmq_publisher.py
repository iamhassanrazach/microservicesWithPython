import json
import os

import pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")


def publish_message(routing_key: str, message: dict) -> None:
    """
    Publish a message to a RabbitMQ queue.

    Opens a short-lived connection, declares the queue (idempotent),
    publishes with delivery_mode=2 (persistent), then closes.
    Errors here are intentionally NOT re-raised — a failed notification
    must never roll back the activity creation.
    """
    try:
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        channel = connection.channel()
        channel.queue_declare(queue=routing_key, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=routing_key,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        connection.close()
        print(f"[rabbitmq] Published to '{routing_key}': {message}")
    except Exception as exc:
        # Log and swallow — messaging failure is non-fatal for the request
        print(f"[rabbitmq] WARNING: could not publish to '{routing_key}': {exc}")
