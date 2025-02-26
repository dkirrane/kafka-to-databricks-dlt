data "databricks_node_type" "smallest" {
  local_disk  = true
  min_cores   = var.min_cores
  gb_per_core = var.gb_per_core
}

data "databricks_spark_version" "latest_lts" {
  long_term_support = true
}

resource "databricks_cluster" "this" {
  cluster_name            = var.cluster_name
  spark_version           = coalesce(var.spark_version, data.databricks_spark_version.latest_lts.id)
  node_type_id            = coalesce(var.node_type_id, data.databricks_node_type.smallest.id)
  autotermination_minutes = var.autotermination_minutes

  dynamic "autoscale" {
    for_each = var.enable_autoscaling ? [1] : []
    content {
      min_workers = var.min_workers
      max_workers = var.max_workers
    }
  }

  num_workers = var.enable_autoscaling ? null : var.num_workers

  spark_conf = var.spark_conf

  custom_tags = var.custom_tags

  spark_env_vars = var.spark_env_vars

  dynamic "library" {
    for_each = var.libraries
    content {
      pypi {
        package = library.value
      }
    }
  }
}