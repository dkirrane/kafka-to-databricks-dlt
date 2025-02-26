"""
Kafka Avro Consumer that reads Avro messages.
- It read messages using the Kafka Topic and Avro Schemas created by Terraform.
- Kafka connection details taken from Azure Key Vault created by Terraform.

Usage:
1. Ensure you have run the `kafka_avro_producer.py` script to produce messages.

2. Run the script:
   python kafka_avro_consumer.py

References: https://github.com/confluentinc/confluent-kafka-python/blob/master/examples/avro_consumer.py
"""

import signal
import time
from kafka_common import *
from confluent_kafka import Consumer
from confluent_kafka.serialization import (
    StringDeserializer,
    SerializationContext,
    MessageField,
)
from confluent_kafka.schema_registry.avro import AvroDeserializer


def main():
    # Register the signal handler
    signal.signal(signal.SIGTERM, signal_handler)

    # Azure Key Vault configuration
    key_vault_name = "databricks-kafka-dr-poc-kv"
    get_config(key_vault_name)

    # Kafka admin client
    admin_client = create_kafka_admin_client()
    ping_kafka_brokers(admin_client)

    # Schema Registry Client
    schema_registry_client = create_schema_registry_client()

    # Key Deserializer (String)
    string_deserializer = StringDeserializer("utf_8")

    avro_deserializer = AvroDeserializer(schema_registry_client)

    # Create Consumer
    print(f"\nCreating Kafka Consumer...")
    kafka_connection_conf = get_kafka_connection_config()
    consumer_conf = {
        "group.id": "user_actions_group",
        "auto.offset.reset": "earliest",  # or 'latest'
        "enable.auto.commit": False,  # Disable auto commit
    }
    consumer_conf.update(kafka_connection_conf)
    # print("consumer_conf: \n", consumer_conf)
    consumer = Consumer(consumer_conf)

    topic = "user-actions"

    consumer.subscribe([topic])

    try:

        while True:

            # SIGINT can't be handled when polling, limit timeout to 1 second.
            msg = consumer.poll(1.0)
            if msg is None:
                continue

            key = string_deserializer(
                msg.key(), SerializationContext(msg.topic(), MessageField.KEY)
            )

            value = avro_deserializer(
                msg.value(), SerializationContext(msg.topic(), MessageField.VALUE)
            )

            offset = msg.offset()

            partition = msg.partition()

            recordReceived = f"Received - Key: ``{key:<30}`` Value: ``{value}`` Partition: ``{partition}`` Offset: ``{offset}``"
            print(recordReceived)
            write_step_summary(recordReceived)

            # sleep for 5 seconds
            time.sleep(5)

    except KeyboardInterrupt:
        print("Interrupted, stopping...")
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
