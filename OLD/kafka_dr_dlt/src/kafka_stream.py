import dlt
from pyspark.sql import functions as F
import os

# Fetching Kafka connection details from Databricks Secrets
SCOPE="dessie-kv-test"
kafka_brokers = dbutils.secrets.get(scope=SCOPE, key="kafka-service-uri-public")
kafka_username = dbutils.secrets.get(scope=SCOPE, key="kafka-admin-username")
kafka_password = dbutils.secrets.get(scope=SCOPE, key="kafka-admin-password")
kafka_ca_cert = dbutils.secrets.get(scope=SCOPE, key="kafka-ca-cert")
kafka_schemaregistry_uri = dbutils.secrets.get(scope=SCOPE, key="kafka-schemaregistry-uri-public")

kafka_topic = "user-actions"  # Replace with your Kafka topic

# CA
script_dir = os.path.dirname(os.path.abspath(__file__))
ca_pem_path = os.path.join(script_dir, "ca.pem")
with open(ca_pem_path, "w") as ca_file:
    ca_file.write(kafka_ca_cert)

# Kafka options with secrets
# https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html
kafka_options = {
    "kafka.bootstrap.servers": kafka_brokers,
    "kafka.security.protocol": "SASL_SSL",
    "kafka.sasl.mechanism": "PLAIN",
    "kafka.sasl.username": kafka_username,
    "kafka.sasl.password": kafka_password,
    "kafka.ssl.ca.location": kafka_password,

    "startingOffsets": "earliest",
    # "startingOffsets": "latest",

    "failOnDataLoss": "false",
    "groupIdPrefix": "kafka-dr-group",
    "includeHeaders": "true",
    "subscribe": kafka_topic,
}

@dlt.table(
    name="user-actions",
    comment="Raw data ingested from Kafka topic",
    table_properties={
        "quality": "bronze",
        "pipelines.reset.allowed": "true" # dev
    }
)
def kafka_raw():
    # Read Kafka stream using the secrets
    kafka_df = (
        spark.readStream
        .format("kafka")
        .options(**kafka_options)
        .load()
    )

    return kafka_df