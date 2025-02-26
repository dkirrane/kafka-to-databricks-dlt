resource "azurerm_key_vault" "this" {
  name                      = var.key_vault_name
  resource_group_name       = var.resource_group_name
  location                  = var.location
  tenant_id                 = data.azurerm_client_config.current.tenant_id
  sku_name                  = "standard"
  enable_rbac_authorization = var.rbac_authorization_enabled
  purge_protection_enabled  = false

  # https://learn.microsoft.com/en-us/azure/databricks/security/secrets/secret-scopes#configure-your-azure-key-vault-instance-for-azure-databricks
  public_network_access_enabled = var.public_access

  network_acls {
    bypass         = "AzureServices"
    default_action = "Allow"
  }

  tags = var.tags
}
