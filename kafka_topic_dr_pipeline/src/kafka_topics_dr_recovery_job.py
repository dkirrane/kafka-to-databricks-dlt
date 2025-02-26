%pip install confluent-kafka==2.5.3
%pip install fastavro==1.9.7

"""
This script reads from the DLT table created by the pipeline.
It sends the recovered messages to a new Kafka topic 'user-actions-recovered'.

It's a WIP and currently has issues:

Py4JJavaError: An error occurred while calling z:org.apache.spark.api.python.PythonRDD.collectAndServe

"""
# Import necessary libraries
import os
from pyspark.sql.functions import col
from confluent_kafka import Producer

# Confluent
# from confluent_kafka.avro.cached_schema_registry_client import CachedSchemaRegistryClient
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka import Producer
from confluent_kafka.serialization import (
    StringSerializer,
    SerializationContext,
    MessageField,
)
from confluent_kafka.schema_registry import topic_record_subject_name_strategy
from confluent_kafka.schema_registry.avro import AvroSerializer

# Databricks secret scope name
SCOPE = "keyvault_secrets"

# Kafka connection secrets
kafka_brokers = dbutils.secrets.get(scope=SCOPE, key="kafka-service-uri-public")
kafka_username = dbutils.secrets.get(scope=SCOPE, key="kafka-admin-username")
kafka_password = dbutils.secrets.get(scope=SCOPE, key="kafka-admin-password")
kafka_ca_cert = dbutils.secrets.get(scope=SCOPE, key="kafka-ca-cert")
kafka_schemaregistry_uri = dbutils.secrets.get(scope=SCOPE, key="kafka-schemaregistry-uri-public")

def get_kafka_connection_config():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ca_pem_path = os.path.join(script_dir, "ca.pem")
    with open(ca_pem_path, "w") as ca_file:
        ca_file.write(kafka_ca_cert)

    # Create the SASL configuration
    conf = {
        "bootstrap.servers": kafka_brokers,
        "security.protocol": "SASL_SSL",
        "sasl.mechanism": "PLAIN",
        "sasl.username": kafka_username,
        "sasl.password": kafka_password,
        "ssl.ca.location": ca_pem_path,
    }
    return conf

# Recover Topic
topic_name = "user-actions"  # Replace with the topic name to filter on
topic_name_new = "user-actions-recovered"  # Replace with your Kafka topic to write to

# Read the DLT table (key, value, schemaId)
dlt_database = "kafka_topic_dr_pipeline"
dlt_table_name = "kafka_topics_dr_raw"
df = spark.sql(f"SELECT * FROM {dlt_database}.{dlt_table_name}")
# df = spark.read.table("dlt_table_name").select("key", "value", "schemaId")

# Filter the dataframe based on the topic name
filtered_df = df.filter(col("topic") == topic_name)

display(df.limit(10))
row_count = df.count()
print(f"Total number of rows: {row_count}")


# Process each partition
def process_partition(partition):

    # COnfig
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ca_pem_path = os.path.join(script_dir, "ca.pem")
    with open(ca_pem_path, "w") as ca_file:
        ca_file.write(kafka_ca_cert)

    # Create the SASL configuration
    conf = {
        "bootstrap.servers": kafka_brokers,
        "security.protocol": "SASL_SSL",
        "sasl.mechanism": "PLAIN",
        "sasl.username": kafka_username,
        "sasl.password": kafka_password,
        "ssl.ca.location": ca_pem_path,
    }

    # Create SchemaRegistryClient
    print(f"\nCreating Kafka Schema Registry client: {kafka_schemaregistry_uri}")
    schema_registry_conf = {"url": kafka_schemaregistry_uri}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    # Create Producer
    print(f"\nCreating Kafka Producer...")
    producer = Producer(conf)

    for row in partition:

        # Lookup DLT row
        key = row["key"]
        value = row["value_deserialized_data"]
        value_schema_id = row["value_schema_id"]

        # Get Avro schema
        value_avro_schema = schema_registry_client.get_by_id(value_schema_id)

        # Key Serializer (String)
        string_serializer = StringSerializer("utf_8")

        # Value Serializer (Avro)
        avro_serializer = AvroSerializer(
            schema_registry_client=schema_registry_client,
            schema_str=value_avro_schema,
            conf={"subject.name.strategy": topic_record_subject_name_strategy},
        )

        print(f"Sending key: {key} and value: {value} to Kafka topic: {topic_name_new}")

        # Send the key and value to the Kafka topic
        producer.produce(
            topic=topic_name_new,
            key=string_serializer(key),
            value=avro_serializer(
                value, SerializationContext(topic_name_new, MessageField.VALUE)
            )
        )

        producer.flush()

# Apply the processing function to each partition
df.foreachPartition(process_partition)
