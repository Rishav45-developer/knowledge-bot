
import json
import os

import pika


QUEUE_NAME = "document_processing"


def publish_document_job(document_id: int) -> None:
    """Publish a document-processing job and confirm broker acceptance."""
    credentials = pika.PlainCredentials(
        os.environ["RABBITMQ_USER"],
        os.environ["RABBITMQ_PASSWORD"],
    )

    parameters = pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
        credentials=credentials,
        heartbeat=60,
        connection_attempts=3,
        retry_delay=2,
    )

    connection = pika.BlockingConnection(parameters)

    try:
        channel = connection.channel()

        channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True,
        )

        # Ask RabbitMQ to confirm that it accepted each published message.
        channel.confirm_delivery()

        message = json.dumps({
            "document_id": document_id,
        })

        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=message.encode("utf-8"),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json",
            ),
            mandatory=True,
        )

        print(f"RabbitMQ accepted job for document {document_id}")

    finally:
        if connection.is_open:
            connection.close()
