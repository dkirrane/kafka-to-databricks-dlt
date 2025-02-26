from databricks.connect import DatabricksSession

#
# Sample using Databricks Connect to connect IDE to Azure Databricks cluster.
# https://learn.microsoft.com/en-gb/azure/databricks/dev-tools/databricks-connect/python/examples
#

spark = DatabricksSession.builder.getOrCreate()

df = spark.read.table("samples.nyctaxi.trips")
df.show(5)