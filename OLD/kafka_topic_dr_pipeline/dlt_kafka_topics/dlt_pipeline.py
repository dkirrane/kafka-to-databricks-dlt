import dlt
from pyspark.sql.functions import *

@dlt.table(
    name="bronze_data",
    comment="Raw data from source"
)
def bronze_data():
    return spark.readStream.format("cloudFiles") \
        .option("cloudFiles.format", "json") \
        .load("/path/to/your/data")

@dlt.table(
    name="silver_data",
    comment="Cleaned and transformed data"
)
def silver_data():
    return dlt.read("bronze_data") \
        .select(
            col("id"),
            col("name"),
            to_date(col("date"), "yyyy-MM-dd").alias("formatted_date")
        )

@dlt.table(
    name="gold_data",
    comment="Aggregated data for analysis"
)
def gold_data():
    return dlt.read("silver_data") \
        .groupBy("formatted_date") \
        .agg(count("id").alias("daily_count"))

def main():
    # In a DLT context, we don't actually "run" the pipeline here.
    # The pipeline is defined by the @dlt.table decorators above.
    # This main function is more for setup and logging.
    print("DLT pipeline is defined and ready to run")

if __name__ == '__main__':
  main()