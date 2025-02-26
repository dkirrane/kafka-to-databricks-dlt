%pip install confluent-kafka

import sys
from confluent_kafka.schema_registry import SchemaRegistryClient

# Databricks secret scope name
SCOPE="keyvault_secrets"

# Function to create the Kafka Connection config
def get_kafka_connection_config():
    # Kafka options with secrets
    # https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html
    kafka_brokers = dbutils.secrets.get(scope=SCOPE, key="kafka-service-uri-public")
    kafka_username = dbutils.secrets.get(scope=SCOPE, key="kafka-admin-username")
    kafka_password = dbutils.secrets.get(scope=SCOPE, key="kafka-admin-password")
    kafka_ca_cert = dbutils.secrets.get(scope=SCOPE, key="kafka-ca-cert")

    sasl_jaas_config = f"kafkashaded.org.apache.kafka.common.security.plain.PlainLoginModule required username=\"{kafka_username}\" password=\"{kafka_password}\";"

    conf = {
        "kafka.bootstrap.servers": kafka_brokers,
        "kafka.security.protocol": "SASL_SSL",
        "kafka.sasl.mechanism": "PLAIN",
        "kafka.sasl.jaas.config": sasl_jaas_config,
        "kafka.ssl.truststore.type": "PEM",
        "kafka.ssl.truststore.certificates": kafka_ca_cert
    }
    return conf

# Function to create the SchemaRegistryClient
def create_schema_registry_client():
    kafka_schemaregistry_uri = dbutils.secrets.get(scope=SCOPE, key="kafka-schemaregistry-uri-public")
    print(f"\nCreating Kafka Schema Registry client: {kafka_schemaregistry_uri}")

    # Create the configuration
    schema_registry_conf = {"url": kafka_schemaregistry_uri}

    # Create the SchemaRegistryClient
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    print("Creating SchemaRegistryClient Done!\n")
    return schema_registry_client


# Function to get schema from Schema Registry
def get_latest_schema(schema_registry_client, subject_name):
    print("\nFetching latest schema for subject: ", subject_name)
    # Get the latest version of the schema for the subject
    schema_info = schema_registry_client.get_latest_version(subject_name)

    schema_id = schema_info.schema_id
    schema_str = schema_info.schema.schema_str
    schema_version = schema_info.version

    # fail if any of the values are None
    if not schema_id or not schema_str or not schema_version:
        print(f"Failed to fetch schema for {subject_name}")
        sys.exit(1)
    else:
        print(f"Schema found for subject_name={subject_name} with id={schema_id} version={schema_version}")
        print(f"{schema_str}\n")

    return schema_str
