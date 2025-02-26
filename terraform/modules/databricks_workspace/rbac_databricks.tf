# Add AzureAD Service Principals to Databricks SPs as Admin
# https://learn.microsoft.com/en-us/azure/databricks/admin/users-groups/service-principals
data "azuread_service_principals" "databricks_sps" {
  display_names = toset(var.service_principals_full_permissions)
}

resource "databricks_service_principal" "service_principals" {
  for_each = toset(var.service_principals_full_permissions)

  application_id = data.azuread_service_principals.databricks_sps.client_ids[index(var.service_principals_full_permissions, each.key)]
  display_name   = data.azuread_service_principals.databricks_sps.display_names[index(var.service_principals_full_permissions, each.key)]

  allow_cluster_create       = true
  allow_instance_pool_create = true
  databricks_sql_access      = true
  workspace_access           = true
  active                     = true
  force                      = true
}

# Add AzureAD Users as Databrick admins
# https://learn.microsoft.com/en-us/azure/databricks/admin/users-groups/users
data "azuread_users" "databricks_admin_users" {
  user_principal_names = toset(var.users_full_permissions)
}

data "databricks_group" "admins" {
  display_name = "admins"
  depends_on = [
    azurerm_databricks_workspace.this,
    databricks_service_principal.service_principals
  ]
}

resource "databricks_user" "admins" {
  for_each     = { for i, v in data.azuread_users.databricks_admin_users.users : i => v }
  user_name    = each.value.mail
  display_name = each.value.display_name

  allow_cluster_create       = true
  allow_instance_pool_create = true
  databricks_sql_access      = true
  workspace_access           = true
  active                     = true
  force                      = true
}

resource "databricks_group_member" "admins" {
  for_each  = databricks_user.admins
  group_id  = data.databricks_group.admins.id
  member_id = each.value.id
}