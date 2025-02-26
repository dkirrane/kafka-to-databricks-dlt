
# https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/databricks_workspace
resource "azurerm_databricks_workspace" "this" {
  name                        = var.workspace_name
  resource_group_name         = var.resource_group_name
  location                    = var.location
  sku                         = var.sku
  managed_resource_group_name = "${var.resource_group_name}-managed"

  custom_parameters {
    no_public_ip        = var.no_public_ip
    virtual_network_id  = var.vnet_id
    public_subnet_name  = var.public_subnet_name
    private_subnet_name = var.private_subnet_name
  }

  tags = var.tags
}

# https://learn.microsoft.com/en-us/azure/databricks/security/secrets/secret-scopes#create-an-azure-key-vault-backed-secret-scope-1
# Use the Databricks CLI:
# databricks secrets list-scopes
# databricks secrets list-secrets <scope-name>
# databricks secrets list-acls <scope-name>
resource "databricks_secret_scope" "keyvault_scope" {
  name         = "keyvault_secrets"
  backend_type = "AZURE_KEYVAULT"
  keyvault_metadata {
    dns_name    = var.key_vault_uri
    resource_id = var.key_vault_id
  }
}
