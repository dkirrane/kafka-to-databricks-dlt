from kafka_topic_dr.databricks_common import *
from kafka_topic_dr.kafka_common import *

import dlt

spark = get_spark()
dbutils = get_dbutils(spark)

# # Schema Registry Client
# schema_registry_client = create_schema_registry_client()

# Kafka connection config
kafka_connection_conf = get_kafka_connection_config(dbutils)

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


@dlt.table(
    name="user_actions",
    comment="Raw data ingested from Kafka topic",
    table_properties={"quality": "bronze", "pipelines.reset.allowed": "true"},  # dev
)
def kafka_raw():
    # Read Kafka stream using the secrets
    kafka_df = spark.readStream.format("kafka").options(**kafka_options).load()

    return kafka_df


def main():
    # In a DLT context, we don't actually "run" the pipeline here.
    # The pipeline is defined by the @dlt.table decorators above.
    # This main function is more for setup and logging.
    print("DLT pipeline is defined and ready to run")


if __name__ == "__main__":
    main()
