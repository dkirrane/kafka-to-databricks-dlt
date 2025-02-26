from confluent_kafka.schema_registry import SchemaRegistryClient
import ssl

import pyspark.sql.functions as fn
from pyspark.sql.types import StringType

binary_to_string = fn.udf(lambda x: str(int.from_bytes(x, byteorder='big')), StringType())

# clickstreamTestDf = (
#   spark
#   .readStream
#   .format("kafka")
#   .option("kafka.bootstrap.servers", confluentBootstrapServers)
#   .option("kafka.security.protocol", "SASL_SSL")
#   .option("kafka.sasl.jaas.config", "kafkashaded.org.apache.kafka.common.security.plain.PlainLoginModule required username='{}' password='{}';".format(confluentApiKey, confluentSecret))
#   .option("kafka.ssl.endpoint.identification.algorithm", "https")
#   .option("kafka.sasl.mechanism", "PLAIN")
#   .option("subscribe", confluentTopicName)
#   .option("startingOffsets", "earliest")
#   .option("failOnDataLoss", "false")
#   .load()
#   .withColumn('key', fn.col("key").cast(StringType()))
#   .withColumn('fixedValue', fn.expr("substring(value, 6, length(value)-5)"))
#   .withColumn('valueSchemaId', binary_to_string(fn.expr("substring(value, 2, 4)")))
#   .select('topic', 'partition', 'offset', 'timestamp', 'timestampType', 'key', 'valueSchemaId','fixedValue')
# )


import pyspark.sql.functions as fn
from pyspark.sql.avro.functions import from_avro

def parseAvroDataWithSchemaId(df, ephoch_id):
  cachedDf = df.cache()

  fromAvroOptions = {"mode":"FAILFAST"}

  def getSchema(id):
    return str(schema_registry_client.get_schema(id).schema_str)

  distinctValueSchemaIdDF = cachedDf.select(fn.col('valueSchemaId').cast('integer')).distinct()

  for valueRow in distinctValueSchemaIdDF.collect():

    currentValueSchemaId = sc.broadcast(valueRow.valueSchemaId)
    currentValueSchema = sc.broadcast(getSchema(currentValueSchemaId.value))

    filterValueDF = cachedDf.filter(fn.col('valueSchemaId') == currentValueSchemaId.value)

    filterValueDF \
      .select('topic', 'partition', 'offset', 'timestamp', 'timestampType', 'key', from_avro('fixedValue', currentValueSchema.value, fromAvroOptions).alias('parsedValue')) \
      .write \
      .format("delta") \
      .mode("append") \
      .option("mergeSchema", "true") \
     .save(deltaTablePath)

display(clickstreamTestDf)