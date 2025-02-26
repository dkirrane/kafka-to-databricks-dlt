variable "cluster_name" {
  description = "The name of the Databricks cluster"
  type        = string
}

variable "spark_version" {
  description = "The Spark version to use for the cluster. If not specified, the latest LTS version will be used."
  type        = string
  default     = null
}

variable "node_type_id" {
  description = "The node type ID for the cluster. If not specified, the smallest available will be used."
  type        = string
  default     = null
}

variable "min_cores" {
  description = "The minimum number of cores for the smallest node type"
  type        = number
  default     = 4
}

variable "gb_per_core" {
  description = "The minimum GB per core for the smallest node type"
  type        = number
  default     = 1
}

variable "autotermination_minutes" {
  description = "Number of minutes of inactivity before the cluster terminates"
  type        = number
  default     = 60
}

variable "enable_autoscaling" {
  description = "Whether to enable autoscaling for the cluster"
  type        = bool
  default     = true
}

variable "min_workers" {
  description = "Minimum number of workers if autoscaling is enabled"
  type        = number
  default     = 1
}

variable "max_workers" {
  description = "Maximum number of workers if autoscaling is enabled"
  type        = number
  default     = 1
}

variable "num_workers" {
  description = "Number of workers if autoscaling is disabled"
  type        = number
  default     = 1
}

variable "spark_conf" {
  description = "Map of Spark configuration options for the cluster"
  type        = map(string)
  default     = {}
}

variable "custom_tags" {
  description = "Map of custom tags to add to the cluster"
  type        = map(string)
  default     = {}
}

variable "spark_env_vars" {
  description = "Map of environment variables to set for Spark on the cluster"
  type        = map(string)
  default     = {}
}

variable "libraries" {
  description = "List of PyPI libraries to install on the cluster"
  type        = list(string)
  default     = []
}