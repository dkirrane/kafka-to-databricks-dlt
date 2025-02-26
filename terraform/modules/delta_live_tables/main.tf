# data "databricks_node_type" "smallest" {
#   local_disk  = true
#   min_cores   = var.min_cores
#   gb_per_core = var.gb_per_core
# }

# data "databricks_spark_version" "latest_lts" {
#   long_term_support = true
# }

# https://registry.terraform.io/providers/databricks/databricks/latest/docs/resources/pipeline
resource "databricks_pipeline" "this" {
  name    = var.pipeline_name
  storage = var.storage_location
  target  = var.target_schema

  #   configuration = merge({
  #     "pipelines.useV2DetailsPage" : "true"
  #   }, var.dlt_configuration)

  #   cluster {
  #     label      = "default"
  #     cluster_id = var.cluster_id
  #   }

  #   library {
  #     notebook {
  #       path = databricks_notebook.dlt_notebook.path
  #     }
  #   }

  continuous = var.continuous_mode

  #   notification = var.notification
}

# resource "databricks_notebook" "dlt_notebook" {
#   path     = var.dlt_notebook_path
#   language = "PYTHON"
#   content  = base64encode(var.dlt_notebook_content)
# }