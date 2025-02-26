# !pip install confluent-kafka

# Databricks notebook source
import dlt

from pyspark.sql.functions import fn
from pyspark.sql.types import StringType
import os
from kafka_common import *

# Schema Registry Client
schema_registry_client = create_schema_registry_client()

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

    "subscribe": kafka_topics
}
kafka_options.update(kafka_connection_conf)

@dlt.table(
    name="user_actions",
    comment="Raw data ingested from Kafka topic",
    table_properties={
        "quality": "bronze",
        "pipelines.reset.allowed": "true" # dev
    }
)
def kafka_raw():
    # https://docs.confluent.io/platform/current/schema-registry/fundamentals/serdes-develop/index.html#wire-format
    # byte 0 = Magic Byte
    # bytes 1->4 = Schema ID as returned by Schema Registry
    # 5-… = Serialized data for the specified schema format (Avro or Protocol Buffers)
    # UDF to help parse bytes into a string
    binary_to_string = fn.udf(lambda x: str(int.from_bytes(x, byteorder='big')), StringType())

    # Read Kafka stream using the secrets
    kafka_df = (
        spark.readStream
        .format("kafka")
        .options(**kafka_options)
        .load()
        .withColumn('key', fn.col("key").cast(StringType()))
        .withColumn('valueSchemaId', binary_to_string(fn.expr("substring(value, 2, 4)")))
        .withColumn('fixedValue', fn.expr("substring(value, 6, length(value)-5)"))
    )

    return kafka_df

# @dlt.table
# def consuming_table():
#     source_df = dlt.read("user_actions")

#     # Perform some transformation
#     transformed_df = source_df.withColumn("new_column", col.lit("example"))

#     return transformed_df