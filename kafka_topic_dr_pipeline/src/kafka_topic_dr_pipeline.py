# Databricks notebook source
%pip install fastavro==1.9.7

# COMMAND ----------

import dlt
from pyspark.sql import functions as F
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
import io
import json
import requests

# Databricks secret scope name
SCOPE = "keyvault_secrets"


# Function to create the Kafka Connection config
def get_kafka_connection_config():
    # Kafka options with secrets
    # https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html
    kafka_brokers = dbutils.secrets.get(scope=SCOPE, key="kafka-service-uri-public")
    kafka_username = dbutils.secrets.get(scope=SCOPE, key="kafka-admin-username")
    kafka_password = dbutils.secrets.get(scope=SCOPE, key="kafka-admin-password")
    kafka_ca_cert = dbutils.secrets.get(scope=SCOPE, key="kafka-ca-cert")

    sasl_jaas_config = f'kafkashaded.org.apache.kafka.common.security.plain.PlainLoginModule required username="{kafka_username}" password="{kafka_password}";'

    conf = {
        "kafka.bootstrap.servers": kafka_brokers,
        "kafka.security.protocol": "SASL_SSL",
        "kafka.sasl.mechanism": "PLAIN",
        "kafka.sasl.jaas.config": sasl_jaas_config,
        "kafka.ssl.truststore.type": "PEM",
        "kafka.ssl.truststore.certificates": kafka_ca_cert,
    }
    return conf

# Kafka connection config
kafka_connection_conf = get_kafka_connection_config()

# Topics
kafka_topics = "user-actions"

# Other Kafka options
kafka_options = {
    "startingOffsets": "earliest",
    # "startingOffsets": "latest",
    # it will stop the stream if there is a break in the sequence of offsets because it assumes data was lost.
    "failOnDataLoss": "false",
    "groupIdPrefix": "kafka-dr-group",
    "includeHeaders": "true",
    "subscribe": kafka_topics,
}
kafka_options.update(kafka_connection_conf)

kafka_schemaregistry_uri = dbutils.secrets.get(
    scope=SCOPE, key="kafka-schemaregistry-uri-public"
)


def fetch_schema_from_registry(schema_id):
    print(f"\nCreating Kafka Schema Registry client: {kafka_schemaregistry_uri}")

    schema_registry_url = f"{kafka_schemaregistry_uri}/schemas/ids/{schema_id}"
    response = requests.get(schema_registry_url)
    if response.status_code != 200:
        raise Exception(
            f"***** schema registry fetch failed..."
        )  # TODO: Remove later. This is for troubleshooting.
    content = response.content.decode("utf-8")
    parsed = json.loads(content)
    schema = json.loads(parsed["schema"])
    return schema


# Function that will fetch a schema from the schema registry by ID
@udf(returnType=StringType())
def get_schema_by_id(schema_id):
    print(f"Fetching schema for ID {schema_id}")
    try:
        schema = fetch_schema_from_registry(schema_id)
        return json.dumps(schema)
    except Exception as e:
        return json.dumps(
            {"error": f"Failed to fetch schema for ID {schema_id}: {str(e)}"}
        )



import fastavro
import traceback

# Function to Deserialise the Avro bytes in the Kafka message
@udf(returnType=StringType())
def deserialise_avro_data_with_schema(schema_json, avro_bytes):
    try:
        print(f"Deserialising {avro_bytes} with schema {schema_json}")
        # parsed_schema = fastavro.parse_schema(schema_json)
        schema = json.loads(schema_json)
        bytes_io = io.BytesIO(avro_bytes)
        record = fastavro.schemaless_reader(bytes_io, schema)
        return record
    except Exception as e:
        # Handle any deserialization issues and return None
        print(f"Failed to deserialize Avro data: {e}")
        # Get the full exception traceback as a string
        exception_string = ''.join(traceback.format_exception(None, e, e.__traceback__)).replace('\n', ' ')
        print(exception_string)
        return f"Failed to deserialize Avro data: {exception_string}"


from pyspark.sql.types import StructType, StructField, IntegerType, BinaryType

# Function to split the Avro payload as per the Avro Wire Format
# https://docs.confluent.io/platform/current/schema-registry/fundamentals/serdes-develop/index.html#wire-format
@udf(returnType=StructType([
    StructField("magic_byte", IntegerType(), True),
    StructField("schema_id", IntegerType(), True),
    StructField("serialized_data", BinaryType(), True)
]))
def parse_serialized_message(serialized_message):
    if serialized_message is None or len(serialized_message) < 5:
        return None, None, None  # Return None for all if message is too short

    magic_byte = serialized_message[0:1]        # First byte
    schema_id_bytes = serialized_message[1:5]   # Next 4 bytes for schema ID
    serialized_data = serialized_message[5:]    # Remainder is the serialized data

    magic_int = int.from_bytes(magic_byte, byteorder="big")
    schema_id_int = int.from_bytes(schema_id_bytes, byteorder="big")

    # schema = get_schema_by_id(schema_id_int)

    return magic_int, schema_id_int, serialized_data

# https://docs.databricks.com/en/delta-live-tables/index.html
# https://docs.databricks.com/en/delta-live-tables/api-guide.html
# https://docs.databricks.com/en/delta-live-tables/properties.html
# https://docs.databricks.com/en/delta-live-tables/python-ref.html
@dlt.table(
    name="kafka_topics_dr_raw",
    comment="Raw Kafka Topic records",
    table_properties={"quality": "bronze", "pipelines.reset.allowed": "true"},  # dev
)
def kafka_topics_dr_raw():
    # Read Kafka topics
    kafka_topics_df = (
        spark.readStream.format("kafka")
        .options(**kafka_options)
        .load()

        # Key
        .withColumn("key", F.col("key").cast(StringType()))

        # Value
        .withColumn("value_parsed", parse_serialized_message(F.col("value")))
        .withColumn("value_magic_byte", F.col("value_parsed.magic_byte"))
        .withColumn("value_schema_id", F.col("value_parsed.schema_id"))
        .withColumn("value_serialized_data", F.col("value_parsed.serialized_data"))
        .drop("value_parsed")

        # Get Value Avro Schema
        .withColumn("value_schema", get_schema_by_id(F.col("value_schema_id")))

        # Deserialise Value Avro data
        .withColumn(
            "value_deserialized_data",
            deserialise_avro_data_with_schema(
                F.col("value_schema"), F.col("value_serialized_data")
            ),
        )

        # Select all columns
        .select("*")
    )

    # print("DLT display\n")
    # display(kafka_topics_df)

    return kafka_topics_df


# @dlt.table
# def kafka_topics_dr_derserialised():
#   df = dlt.readStream("kafka_topics_dr_raw")

#   print("DLT display\n")
#   display(df)

#   return df
