variable "workspace_name" {
  description = "The name of the Azure Databricks workspace"
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

variable "sku" {
  description = "The SKU to use for the Azure Databricks workspace"
  type        = string
  default     = "trial"
  validation {
    condition     = contains(["standard", "premium", "trial"], var.sku)
    error_message = "Valid values for sku are 'standard', 'premium', or 'trial'."
  }
}

variable "managed_resource_group_name" {
  description = "The name of the resource group where Azure should place the managed Databricks resources"
  type        = string
  default     = null
}

variable "no_public_ip" {
  description = "Specifies whether to deploy Azure Databricks workspace with no public IP"
  type        = bool
  default     = false
}

variable "vnet_id" {
  description = "The ID of the Virtual Network where this Azure Databricks workspace should be created"
  type        = string
  default     = null
}

variable "public_subnet_name" {
  description = "The name of the Public Subnet within the Virtual Network"
  type        = string
  default     = null
}

variable "private_subnet_name" {
  description = "The name of the Private Subnet within the Virtual Network"
  type        = string
  default     = null
}

variable "key_vault_name" {
  description = "The name of the Azure Key Vault (for Azure Key Vault-backed secret scope)"
  type        = string
  default     = null
}

variable "key_vault_id" {
  description = "The ID of the Azure Key Vault (for Azure Key Vault-backed secret scope)"
  type        = string
  default     = null
}

variable "key_vault_uri" {
  description = "The URI of the Azure Key Vault (for Azure Key Vault-backed secret scope)"
  type        = string
  default     = null
}

variable "groups_full_permissions" {
  description = "A List of AzureAD security Groups that will get full Access Policy permissions to this KeyVault"
  type        = list(string)
  default     = ["AXP-ServicePrincipals", "AZ-CCaaS-TeamCloudPlatform", "AZ-CCaaS-TeamCloudOps", "AZ-CCaaS-TeamCICD", "CloudPlatform", "TeamCloudOps", "TeamCiCd", "Developers"]
}

variable "users_full_permissions" {
  description = "A List of AzureAD users that will get full permissions on the Azure Databricks workspace"
  type        = list(string)
  default     = ["dkirrane@valdis.dkirrane.com"]
}

variable "service_principals_full_permissions" {
  description = "A List of AzureAD SPs that will get full permissions on the Azure Databricks workspace"
  type        = list(string)
  #   default     = ["GitHubActionsSP", "TerraformSP"] # GitHubActionsSP is automatically added since it's used by Terraform
  default = ["TerraformSP"]
}

variable "tags" {
  description = "A mapping of tags to assign to the resource"
  type        = map(string)
  default     = {}
}