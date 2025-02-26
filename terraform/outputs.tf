output "resource_group_name" {
  value = module.resource_group.resource_group_name
}

output "key_vault_name" {
  value = var.key_vault_enabled ? module.key_vault[0].key_vault_name : null
}

output "key_vault_id" {
  value = var.key_vault_enabled ? module.key_vault[0].key_vault_id : null
}

output "key_vault_uri" {
  value = var.key_vault_enabled ? module.key_vault[0].key_vault_uri : null
}

# output "aiven" {
#   value = var.aiven_kafka_enabled ? nonsensitive(module.aiven_kafka[0].aiven_kafka) : null
#   sensitive   = false
# }

output "databricks_workspace_url" {
  value = var.databricks_workspace_enabled ? module.databricks_workspace[0].workspace_url : null
}

output "databricks_cluster_id" {
  value = var.databricks_cluster_enabled ? module.databricks_cluster[0].cluster_id : null
}

output "delta_live_tables_pipeline_id" {
  value = var.databricks_dlt_enabled ? module.databricks_dlt[0].pipeline_id : null
}