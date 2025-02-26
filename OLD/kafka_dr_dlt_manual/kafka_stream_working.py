from pyspark.sql.functions import col
import os

# Load Kafka connection details from Databricks secret scope
SCOPE="keyvault_secrets"
kafka_brokers = dbutils.secrets.get(scope=SCOPE, key="kafka-service-uri-public")
kafka_username = dbutils.secrets.get(scope=SCOPE, key="kafka-admin-username")
kafka_password = dbutils.secrets.get(scope=SCOPE, key="kafka-admin-password")
kafka_ca_cert = dbutils.secrets.get(scope=SCOPE, key="kafka-ca-cert")
kafka_schemaregistry_uri = dbutils.secrets.get(scope=SCOPE, key="kafka-schemaregistry-uri-public")

sasl_jaas_config = f"kafkashaded.org.apache.kafka.common.security.plain.PlainLoginModule required username=\"{kafka_username}\" password=\"{kafka_password}\";"

# Topic
kafka_topic = "user-actions"

# Kafka options with secrets
# https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html
kafka_options = {
    "kafka.bootstrap.servers": kafka_brokers,
    "kafka.security.protocol": "SASL_SSL",
    "kafka.sasl.mechanism": "PLAIN",
    # "kafka.sasl.username": kafka_username,
    # "kafka.sasl.password": kafka_password,
    "kafka.sasl.jaas.config": sasl_jaas_config,
    "kafka.ssl.truststore.type": "PEM",
    "kafka.ssl.truststore.certificates": kafka_ca_cert,

    "startingOffsets": "earliest",
    # "startingOffsets": "latest",

    "failOnDataLoss": "false",
    "groupIdPrefix": "kafka-dr-group",
    "includeHeaders": "true",
    "subscribe": kafka_topic,
}

# Read from Kafka topic
df = spark \
  .readStream \
  .format("kafka") \
  .options(**kafka_options) \
  .load()

display(df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)"))