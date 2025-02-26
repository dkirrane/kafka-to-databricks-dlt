"""
Kafka Avro Producer that writes Avro messages.
- It write messages using the Kafka Topic and Avro Schemas created by Terraform.
- Kafka connection details taken from Azure Key Vault created by Terraform.

Usage:
1. Ensure you have the required packages installed:
   pip install confluent-kafka avro-python3
   pip install azure-identity azure-keyvault-secrets

2. Run the script:
   python kafka_avro_producer.py

References: https://github.com/confluentinc/confluent-kafka-python/blob/master/examples/avro_producer.py
"""

import signal
import time
from uuid import uuid4
from kafka_common import *
from kafka_faker import *
from confluent_kafka import Producer
from confluent_kafka.serialization import (
    StringSerializer,
    SerializationContext,
    MessageField,
)
from confluent_kafka.schema_registry import topic_record_subject_name_strategy
from confluent_kafka.schema_registry.avro import AvroSerializer


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

    # Key Serializer (String)
    string_serializer = StringSerializer("utf_8")

    # Create Producer
    print(f"\nCreating Kafka Producer...")
    producer_conf = get_kafka_connection_config()
    producer = Producer(producer_conf)

    topic = "user-actions"

    #
    # Create some fake events
    #
    try:
        while True:

            for func in [
                generate_user_created,
                generate_user_login_attempt,
                generate_order_placed,
                generate_payment_processed,
                generate_shipment_status,
                generate_inventory_update,
            ]:
                schema, record = func(schema_registry_client)
                print(f"Function: {func.__name__}")
                print(f"Schema: {schema}")
                print(f"Record: {record}")
                print()
                # Value Serializer (Avro)
                avro_serializer = AvroSerializer(
                    schema_registry_client=schema_registry_client,
                    schema_str=schema,
                    conf={"subject.name.strategy": topic_record_subject_name_strategy},
                )
                # Producer
                # key = str(uuid4())
                key = get_next_key()
                value = record
                producer.produce(
                    topic=topic,
                    key=string_serializer(key),
                    value=avro_serializer(
                        value, SerializationContext(topic, MessageField.VALUE)
                    ),
                    on_delivery=delivery_report,
                )
                producer.flush()
                recordSent = f"Sent - Key: ``{key:<30}`` Value: ``{value}``"
                print(recordSent)
                write_step_summary(recordSent)

                # sleep for 5 seconds
                time.sleep(5)

    except KeyboardInterrupt:
        print("Interrupted, stopping...")
    finally:
        producer.flush()
        producer.close()

if __name__ == "__main__":
    main()
