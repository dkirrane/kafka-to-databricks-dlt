output "workspace_id" {
  description = "The ID of the Azure Databricks workspace"
  value       = azurerm_databricks_workspace.this.id
}

output "workspace_url" {
  description = "The workspace URL which is of the format 'adb-{workspaceId}.{random}.azuredatabricks.net'"
  value       = azurerm_databricks_workspace.this.workspace_url
}

output "workspace_managed_resource_group_id" {
  description = "The ID of the Managed Resource Group for this Azure Databricks workspace"
  value       = azurerm_databricks_workspace.this.managed_resource_group_id
}