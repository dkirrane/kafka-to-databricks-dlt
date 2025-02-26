output "vnet_id" {
  description = "The ID of the created virtual network"
  value       = azurerm_virtual_network.this.id
}

output "vnet_name" {
  description = "The name of the created virtual network"
  value       = azurerm_virtual_network.this.name
}

output "databricks_subnet_id" {
  description = "The ID of the created Databricks subnet"
  value       = azurerm_subnet.databricks.id
}

output "databricks_subnet_name" {
  description = "The name of the created Databricks subnet"
  value       = azurerm_subnet.databricks.name
}

output "databricks_nsg_id" {
  description = "The ID of the created Network Security Group for Databricks"
  value       = azurerm_network_security_group.databricks.id
}