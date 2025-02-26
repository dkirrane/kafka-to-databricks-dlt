# Current User
data "azurerm_client_config" "current" {}

resource "azurerm_role_assignment" "current_full_permissions" {
  scope                = azurerm_databricks_workspace.this.id
  role_definition_name = "Owner"
  principal_id         = data.azurerm_client_config.current.object_id
}

# Groups
data "azuread_groups" "full_permissions" {
  display_names = toset(var.groups_full_permissions)
}

resource "azurerm_role_assignment" "group_full_permissions" {
  for_each = toset(var.groups_full_permissions)

  scope                = azurerm_databricks_workspace.this.id
  role_definition_name = "Owner"
  principal_id         = data.azuread_groups.full_permissions.object_ids[index(var.groups_full_permissions, each.key)]
}

# Users
data "azuread_users" "full_permissions" {
  user_principal_names = toset(var.users_full_permissions)
}

resource "azurerm_role_assignment" "user_full_permissions" {
  for_each = toset(var.users_full_permissions)

  scope                = azurerm_databricks_workspace.this.id
  role_definition_name = "Owner"
  principal_id         = data.azuread_users.full_permissions.object_ids[index(var.users_full_permissions, each.key)]
}