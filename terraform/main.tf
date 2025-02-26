locals {
  name_prefix = "${var.prefix}-${var.workspace}"
}

module "resource_group" {
  source              = "./modules/azure_resource_group"
  resource_group_name = "${local.name_prefix}-rg"
  location            = var.location
  tags                = var.tags
}

module "virtual_network" {
  count               = var.vnet_enabled ? 1 : 0
  source              = "./modules/azure_virtual_network"
  resource_group_name = module.resource_group.resource_group_name
  vnet_name           = "${local.name_prefix}-vnet"
  location            = var.location
  tags                = var.tags
}

module "key_vault" {
  count  = var.key_vault_enabled ? 1 : 0
  source = "./modules/azure_key_vault"

  resource_group_name = module.resource_group.resource_group_name
  location            = var.location
  key_vault_name      = "${local.name_prefix}-kv"
  public_access       = var.key_vault_allow_public_access

  tags = var.tags
}

module "aiven_kafka" {
  count  = var.aiven_kafka_enabled ? 1 : 0
  source = "./modules/aiven_kafka"

  project_name           = var.aiven_project
  location               = var.location
  kafka_plan             = var.aiven_kafka_plan
  service_name           = "${local.name_prefix}-kafka"
  public_access          = var.aiven_allow_public_access
  tiered_storage_enabled = var.aiven_tiered_storage_enabled

  key_vault_id = module.key_vault[0].key_vault_id

  tags = var.tags
}

module "databricks_workspace" {
  count  = var.databricks_workspace_enabled ? 1 : 0
  source = "./modules/databricks_workspace"

  workspace_name      = "${local.name_prefix}-dbw"
  resource_group_name = module.resource_group.resource_group_name
  location            = var.location
  sku                 = var.databricks_workspace_sku

  key_vault_name = module.key_vault[0].key_vault_name
  key_vault_id   = module.key_vault[0].key_vault_id
  key_vault_uri  = module.key_vault[0].key_vault_uri

  # Optional: VNet integration
  #   vnet_id             = module.resource_group.vnet_id
  #   public_subnet_name  = module.resource_group.vnet_id
  #   private_subnet_name = module.resource_group.vnet_id

  tags = var.tags
}

module "databricks_cluster" {
  count  = var.databricks_cluster_enabled ? 1 : 0
  source = "./modules/databricks_cluster"

  cluster_name = "${local.name_prefix}-dbc"

  spark_version           = "15.4.x-cpu-ml-scala2.12"
  node_type_id            = "Standard_DS3_v2"
  min_cores               = 1
  gb_per_core             = 1
  autotermination_minutes = 15
  enable_autoscaling      = true
  min_workers             = 1
  max_workers             = 1
  #   spark_conf = {
  #     "spark.databricks.cluster.profile": "singleNode"
  #   }
  #   spark_env_vars = {
  #     PYSPARK_PYTHON = "/databricks/python3/bin/python3"
  #   }
  #   libraries = [
  #     "numpy",
  #     "pandas",
  #     "scikit-learn"
  #   ]
  depends_on = [module.databricks_workspace]
}

module "databricks_dlt" {
  count  = var.databricks_dlt_enabled ? 1 : 0
  source = "./modules/delta_live_tables"

  # DLT configuration
  pipeline_name    = "${local.name_prefix}-dlt-pipeline"
  storage_location = "/mnt/datalake/${local.name_prefix}-dlt-pipeline"
  target_schema    = "target_schema"
  continuous_mode  = true

  #   notebook_path    = "/Shared/dlt_pipeline_notebook"
  #   notebook_content = <<-EOT
  #     import dlt
  #     from pyspark.sql.functions import *

  #     @dlt.table
  #     def my_dlt_table():
  #         return spark.readStream.format("kafka")
  #             .option("kafka.bootstrap.servers", "KAFKA_BROKER:9092")
  #             .option("subscribe", "my-topic")
  #             .load()
  #   EOT

  #   dlt_configuration = {
  #     "pipelines.enable.schema_validation" : "true"
  #   }

  tags = var.tags
}