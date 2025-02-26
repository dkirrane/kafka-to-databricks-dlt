variable "key_vault_name" {
  description = "The name of the Key Vault."
  type        = string
}

variable "resource_group_name" {
  description = "The name of the resource group in which to create the Azure Databricks workspace"
  type        = string
}

variable "location" {
  description = "The Azure region where the workspace should be created"
  type        = string
}

variable "public_access" {
  description = "Whether public network access is allowed for this Key Vault."
  type        = bool
  default     = false
}

variable "rbac_authorization_enabled" {
  type        = bool
  description = "Whether the Key Vault uses Role Based Access Control (RBAC) for authorization of data actions instead of access policies."
  default     = true
}

variable "groups_full_permissions" {
  description = "A List of AzureAD security Groups that will get Key Vault Administrator role"
  type        = list(string)
  default     = ["AXP-ServicePrincipals", "AZ-CCaaS-TeamCloudPlatform", "AZ-CCaaS-TeamCloudOps", "AZ-CCaaS-TeamCICD", "CloudPlatform", "TeamCloudOps", "TeamCiCd", "Developers"]
}

variable "users_full_permissions" {
  description = "A List of AzureAD users that will get Key Vault Administrator role"
  type        = list(string)
  default     = ["dkirrane@valdis.dkirrane.com"]
}

variable "tags" {
  description = "Tags to apply to the resources."
  type        = map(string)
  default     = {}
}
