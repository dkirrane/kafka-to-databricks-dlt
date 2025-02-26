%pip install confluent-kafka
%restart_python or dbutils.library.restartPython()
from confluent_kafka.schema_registry import SchemaRegistryClient

import dlt
from pyspark.sql import functions as F
from pyspark.sql.types import StringType
from pyspark.sql.avro.functions import from_avro

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

def parseAvroDataWithSchemaId(schema_id, value):
    # Cache this so that when the logic below uses the Dataframe more than once the data is not pulled from the topic again
    # cachedDf = df.cache()

    # Set the option for what to do with corrupt data in from_avro - either stop on the first failure it finds (FAILFAST) or just set corrupt data to null (PERMISSIVE)
    fromAvroOptions = {"mode":"FAILFAST"}
    #fromAvroOptions= ("mode":"PERMISSIVE")

    # Function that will fetch a schema from the schema registry by ID
    def get_schema_by_id(schema_id):
        print("\nFetching latest schema for id: ", id)
        schema = str(schema_registry_client.get_schema(id).schema_str)
        print(f"{schema}")
        return schema

    from_avro(value, currentValueSchema.value, fromAvroOptions)

# Kafka connection config
kafka_connection_conf = get_kafka_connection_config()

# Schema Registry Client
schema_registry_client = create_schema_registry_client()

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
    name="kafka_topics_dr_raw",
    comment="Raw Kafka Topic records",
    table_properties={
        "quality": "bronze",
        "pipelines.reset.allowed": "true" # dev
    }
)
def kafka_topics_dr_raw():
    # https://docs.confluent.io/platform/current/schema-registry/fundamentals/serdes-develop/index.html#wire-format
    # byte 0 = Magic Byte
    # bytes 1->4 = Schema ID as returned by Schema Registry
    # 5-… = Serialized data for the specified schema format (Avro or Protocol Buffers)
    # UDF to help parse bytes into a string
    binary_to_string = F.udf(lambda x: str(int.from_bytes(x, byteorder='big')), StringType())

    # Read Kafka stream using the secrets
    kafka_topics_df = (
        spark.readStream
        .format("kafka")
        .options(**kafka_options)
        .load()
        .withColumn('key', F.col("key").cast(StringType()))
        .withColumn('valueSchemaId', binary_to_string(F.expr("substring(value, 2, 4)")))
        .withColumn('fixedValue', F.expr("substring(value, 6, length(value)-5)"))
    )

    display(kafka_topics_df)

    return kafka_topics_df

@dlt.table(
    comment="Deserialised Kafka Topic records",
    # spark_conf={"pipelines.trigger.interval": "0 seconds"}
)
def kafka_dr_deserialised():
    kafka_topics_dez_df = (
        dlt.readStream("kafka_topics_dr_raw")
        # .withColumn("value64", base64("value")) # encode binary to base64 to prevent parsing errors when passing to UDF
        # .drop("value")
        .withColumn("deserialisedValue", parseAvroDataWithSchemaId(F.col("valueSchemaId"), F.col("fixedValue")))
        # .withColumn("is_quarantined", from_json(col("value"), StructType([StructField(quarantined_field, StringType())])).getItem(quarantined_field))
        # .drop("value64")
        .withColumn("insert_ts", current_timestamp())
    )

    display(kafka_topics_dez_df)

    return kafka_topics_dez_df
