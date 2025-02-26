from pyspark.sql import SparkSession
from pyspark.dbutils import DBUtils


# Create a new Databricks Connect session. If this fails,
# check that you have configured Databricks Connect correctly.
# See https://docs.databricks.com/dev-tools/databricks-connect.html.
def get_spark() -> SparkSession:
    print(f"\nCreating Databricks SparkSession")
    try:
        from databricks.connect import DatabricksSession

        return DatabricksSession.builder.getOrCreate()
        # return DatabricksSession.builder.profile("DEFAULT").getOrCreate()
    except ImportError:
        return SparkSession.builder.getOrCreate()


def get_dbutils(spark):
    print(f"\nCreating Databricks Utilities")
    dbutils = DBUtils(spark)
    return dbutils
# #
# # See https://docs.databricks.com/en/dev-tools/databricks-connect/python/databricks-utilities.html
# def get_dbutils() -> DBUtils:
#     print(f"\nCreating Databricks Utilities")
#     from databricks.sdk import WorkspaceClient

#     w = WorkspaceClient()
#     dbutils = w.dbutils

#     for secret_scope in dbutils.secrets.listScopes():
#         for secret_metadata in dbutils.secrets.list(secret_scope.name):
#             print(f"found {secret_metadata.key} secret in {secret_scope.name} scope")

#     return dbutils
