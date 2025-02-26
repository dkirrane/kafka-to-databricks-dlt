import os
import sys
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.avro.cached_schema_registry_client import (
    CachedSchemaRegistryClient,
)
from confluent_kafka.admin import AdminClient
from confluent_kafka import KafkaException
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the ca.pem file
ca_pem_path = os.path.join(script_dir, "ca.pem")

# If public Aiven endpoint
public_access = True

# Secret Names
# ternary operator to set the secret name based on the public_access variable
KAFKA_BOOTSTRAP_SERVERS = (
    "kafka-service-uri-public" if public_access else "kafka-service-uri"
)
KAFKA_USERNAME = "kafka-admin-username"
KAFKA_PASSWORD = "kafka-admin-password"
KAFKA_CA_CERT = "kafka-ca-cert"
KAFKA_SCHEMA_REGISTRY_URI = (
    "kafka-schemaregistry-uri-public" if public_access else "kafka-schemaregistry-uri"
)


# Define a signal handler
def signal_handler(sig, frame):
    print("SIGTERM received, stopping...")
    sys.exit(0)


# Function to get a secret from Azure Key Vault
def get_secret_from_keyvault(key_vault_name, secret_name):
    try:
        vault_url = f"https://{key_vault_name}.vault.azure.net/"
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=vault_url, credential=credential)
        secret = client.get_secret(secret_name)
        return secret.value
    except Exception as e:
        print(f"Error retrieving secret {secret_name} from Key Vault: {e}")
        sys.exit(1)


# Get Kafka connection details from Azure Key Vault
def get_config(key_vault_name):
    print(f"\nGetting Kafka connection details from Azure Key Vault: {key_vault_name}")
    for secret in [
        KAFKA_BOOTSTRAP_SERVERS,
        KAFKA_USERNAME,
        KAFKA_PASSWORD,
        KAFKA_CA_CERT,
        KAFKA_SCHEMA_REGISTRY_URI,
    ]:
        secret_value = get_secret_from_keyvault(key_vault_name, secret)
        globals()[secret] = secret_value

        # Write to ca.pem if secret name is 'kafka-ca-cert' for Python 'ssl_cafile'
        if secret == KAFKA_CA_CERT:
            with open(ca_pem_path, "w") as ca_file:
                ca_file.write(secret_value)

    print("Retrieved all Kafka connection details!\n")


def get_kafka_connection_config():
    # Create the SASL configuration
    conf = {
        "bootstrap.servers": globals().get(KAFKA_BOOTSTRAP_SERVERS),
        "security.protocol": "SASL_SSL",
        "sasl.mechanism": "PLAIN",
        "sasl.username": globals().get(KAFKA_USERNAME),
        "sasl.password": globals().get(KAFKA_PASSWORD),
        "ssl.ca.location": ca_pem_path,
    }
    return conf


def create_kafka_admin_client():
    bootstrap_servers = globals().get(KAFKA_BOOTSTRAP_SERVERS)
    print(f"\nCreating Kafka Admin client for : {bootstrap_servers}")

    conf = get_kafka_connection_config()

    # Create the AdminClient
    admin_client = AdminClient(conf)

    print("Creating AdminClient Done!\n")
    return admin_client


def create_schema_registry_client():
    kafka_schema_registry_uri = globals()[KAFKA_SCHEMA_REGISTRY_URI]
    print(f"\nCreating Kafka Schema Registry client: {kafka_schema_registry_uri}")

    # Create the configuration
    schema_registry_conf = {"url": kafka_schema_registry_uri}

    # Create the SchemaRegistryClient
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    print("Creating SchemaRegistryClient Done!\n")
    return schema_registry_client


def ping_kafka_brokers(admin_client):
    print("\nPinging Kafka Brokers...")
    try:
        # List topics to test the connection
        cluster_metadata = admin_client.list_topics(timeout=10)

        print("Successfully connected to Kafka cluster.")
        print(f"Broker(s): {', '.join(map(str, cluster_metadata.brokers.keys()))}")
        print(f"Topics: {', '.join(cluster_metadata.topics.keys())}")

        print("Kafka Brokers connection ok!\n")
    except KafkaException as e:
        print(f"Failed to connect to Kafka cluster: {e}")
        sys.exit(1)


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
        print(
            f"Schema found for subject_name={subject_name} with id={schema_id} version={schema_version}"
        )
        print(f"{schema_str}\n")

    return schema_str


def delivery_report(err, msg):
    """
    Reports the failure or success of a message delivery.

    Args:
        err (KafkaError): The error that occurred on None on success.

        msg (Message): The message that was produced or failed.

    Note:
        In the delivery report callback the Message.key() and Message.value()
        will be the binary format as encoded by any configured Serializers and
        not the same object that was passed to produce().
        If you wish to pass the original object(s) for key and value to delivery
        report callback we recommend a bound callback or lambda where you pass
        the objects along.
    """

    if err is not None:
        print("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    print(
        "User record {} successfully produced to {} [{}] at offset {}".format(
            msg.key(), msg.topic(), msg.partition(), msg.offset()
        )
    )


def write_step_summary(message):
    github_step_summary = os.getenv("GITHUB_STEP_SUMMARY")
    if github_step_summary:
        if os.access(github_step_summary, os.W_OK):
            with open(github_step_summary, "a") as f:
                f.write(message + "\n")
        else:
            print(message)
    else:
        print(message)
