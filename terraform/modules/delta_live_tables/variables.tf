variable "pipeline_name" {
  description = "The name of the Delta Live Table pipeline"
  type        = string
}

variable "storage_location" {
  description = "The storage location for the Delta Live Table pipeline"
  type        = string
}

variable "target_schema" {
  description = "The target schema for the Delta Live Table pipeline"
  type        = string
}

# variable "cluster_id" {
#   description = "(Required) The ID of the Cluster to run the pipeline."
#   type        = string
# }

variable "configuration" {
  description = "Additional configuration for the Delta Live Table pipeline"
  type        = map(string)
  default     = {}
}

variable "continuous_mode" {
  description = "Whether to run the Delta Live Table pipeline in continuous mode"
  type        = bool
  default     = false
}

# variable "notebook_path" {
#   description = "The path where the DLT notebook will be created"
#   type        = string
# }

# variable "notebook_content" {
#   description = "The content of the DLT notebook"
#   type        = string
# }

# variable "notification" {
#   description = "Notification configuration"
#   type        = map(string)
#   default = {
#     email_recipients = ["dkirrane@dkirrane.com"]
#     alerts = [
#       "on-update-failure",
#       "on-update-fatal-failure",
#       "on-update-success",
#       "on-flow-failure"
#     ]
#   }
# }

variable "tags" {
  description = "Custom tags for the Delta Live Table pipeline cluster"
  type        = map(string)
  default     = {}
}