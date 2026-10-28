
import json
import os
import time

import pika

from app.worker.processor import process_document


QUEUE_NAME = "document_processing"
DEAD_QUEUE = "document_processing_failed"
MAX_RETRIES = 3


def connect_to_rabbitmq():
    credentials = pika.PlainCredentials(
        os.environ["RABBITMQ_USER"],
        os.environ["RABBITMQ_PASSWORD"],
    )

    parameters = pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
        credentials=credentials,
        heartbeat=60,
        connection_attempts=5,
        retry_delay=3,
    )

    return pika.BlockingConnection(parameters)


def main():
    while True:
        connection = None

        try:
            connection = connect_to_rabbitmq()
            channel = connection.channel()

            channel.queue_declare(
                queue=QUEUE_NAME,
                durable=True,
            )

            channel.queue_declare(
                queue=DEAD_QUEUE,
                durable=True,
            )

            # Process one document at a time.
            channel.basic_qos(prefetch_count=1)

            def callback(ch, method, properties, body):
                headers = properties.headers or {}

                try:
                    message = json.loads(body.decode("utf-8"))
                    document_id = int(message["document_id"])

                    retries = int(headers.get("x-retries", 0))

                    print(
                        f"Processing document {document_id}, "
                        f"attempt {retries + 1}"
                    )

                    process_document(document_id)

                    print(
                        f"Document {document_id} processed successfully"
                    )

                    ch.basic_ack(
                        delivery_tag=method.delivery_tag
                    )

                except Exception as error:
                    print(f"Document processing failed: {error}")

                    try:
                        retries = int(headers.get("x-retries", 0))

                        if retries < MAX_RETRIES:
                            destination = QUEUE_NAME
                            next_retries = retries + 1
                            print(
                                f"Retrying job "
                                f"({next_retries}/{MAX_RETRIES})"
                            )
                        else:
                            destination = DEAD_QUEUE
                            next_retries = retries
                            print(
                                "Maximum retries reached. "
                                "Sending job to failed queue."
                            )

                        # Publish the replacement before acknowledging
                        # the original message.
                        ch.basic_publish(
                            exchange="",
                            routing_key=destination,
                            body=body,
                            properties=pika.BasicProperties(
                                delivery_mode=2,
                                content_type="application/json",
                                headers={
                                    **headers,
                                    "x-retries": next_retries,
                                    "last-error": str(error)[:500],
                                },
                            ),
                            mandatory=True,
                        )

                        ch.basic_ack(
                            delivery_tag=method.delivery_tag
                        )

                    except Exception as publish_error:
                        print(
                            "Could not publish retry/failure message: "
                            f"{publish_error}"
                        )

                        # Requeue the original if replacement publishing
                        # fails. This can retry again after reconnection.
                        ch.basic_nack(
                            delivery_tag=method.delivery_tag,
                            requeue=True,
                        )

            channel.basic_consume(
                queue=QUEUE_NAME,
                on_message_callback=callback,
            )

            print("Waiting for document-processing messages...")
            channel.start_consuming()

        except Exception as error:
            print(f"RabbitMQ connection/consumer error: {error}")
            time.sleep(5)

        finally:
            if connection is not None and connection.is_open:
                connection.close()


if __name__ == "__main__":
    main()
