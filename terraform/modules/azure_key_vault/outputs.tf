output "key_vault_id" {
  description = "The ID of the created Key Vault."
  value       = azurerm_key_vault.this.id

  # Prevents rbac being destroyed before secrets are destroyed
  depends_on = [
    azurerm_role_assignment.current_owner,
    azurerm_role_assignment.group_full_permissions,
    azurerm_role_assignment.databricks
  ]
}

output "key_vault_name" {
  description = "The name of the created Key Vault."
  value       = azurerm_key_vault.this.name
}

output "key_vault_uri" {
  description = "The URI of the created Key Vault."
  value       = azurerm_key_vault.this.vault_uri
}
