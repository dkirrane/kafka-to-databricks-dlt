prefix    = "databricks-kafka-dr"
workspace = "poc"

# Region
location = "eastus2"

# Virtual Network
vnet_enabled = false

# Key Vault
key_vault_enabled             = true
key_vault_allow_public_access = true

# Aiven Kafka
aiven_kafka_enabled          = true
aiven_project                = "dkirrane-test"
aiven_kafka_plan             = "startup-2" # "business-4"
aiven_allow_public_access    = true
aiven_tiered_storage_enabled = true

# Databricks workspace
databricks_workspace_enabled = false
databricks_workspace_sku     = "trial"
# databricks_workspace_sku     = "standard"
# databricks_workspace_sku     = "premium"

# Databricks cluster
databricks_cluster_enabled = false

# Databricks Delta Live Table (DLT)
databricks_dlt_enabled = false

# Resource tags
tags = {
  Owner   = "dkirrane"
  Team    = "Platform"
  Purpose = "Aiven Kafka Topic DR PoC"
}