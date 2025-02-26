variable "prefix" {
  description = "Resource name prefix"
  type        = string
}

variable "workspace" {
  description = "The Terraform workspace name"
  type        = string
}

variable "location" {
  description = "The Azure region where resources will be created"
  type        = string
  default     = "East US"
}

variable "vnet_enabled" {
  description = "Toggle to enable/disable vNet creation"
  type        = bool
  default     = false
}

#
# Azure Key Vault
#
variable "key_vault_enabled" {
  description = "Toggle to enable/disable KeyVault creation"
  type        = bool
  default     = false
}

variable "key_vault_allow_public_access" {
  description = "Allow access to Key Vault from Databricks"
  type        = bool
  default     = false
}

#
# Aiven Kafka
#
variable "aiven_kafka_enabled" {
  description = "Toggle to enable/disable Aiven Kafka service creation"
  type        = bool
  default     = false
}

variable "aiven_project" {
  description = "Aiven project Name"
  type        = string
}

variable "aiven_kafka_plan" {
  description = "Aiven Kafka Plan"
  type        = string
}

variable "aiven_allow_public_access" {
  description = "Allow public access to Kafka service"
  type        = bool
}

variable "aiven_tiered_storage_enabled" {
  description = "Enable tiered storage"
  type        = bool
  default     = false
}

#
# Databricks
#

variable "databricks_workspace_enabled" {
  description = "Toggle to enable/disable Databricks workspace creation"
  type        = bool
  default     = false
}

variable "databricks_workspace_sku" {
  description = "The sku to use for the Databricks Workspace. Possible values are standard, premium, or trial."
  type        = string
  default     = "trial"
}

variable "databricks_cluster_enabled" {
  description = "Toggle to enable/disable Databricks cluster creation"
  type        = bool
  default     = false
}

variable "databricks_dlt_enabled" {
  description = "Toggle to enable/disable Databricks Delta Live Table (DLT) pipeline creation"
  type        = bool
  default     = false
}

variable "tags" {
  description = "A mapping of tags to assign to the resources"
  type        = map(string)
  default     = {}
}