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

    # display(kafka_topics_df)

    return kafka_topics_df