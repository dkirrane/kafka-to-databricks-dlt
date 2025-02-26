variable "project_name" {
  description = "The name of the Aiven project"
  type        = string
}

variable "location" {
  description = "The Azure region where the Aiven services should be created"
  type        = string
}

variable "kafka_plan" {
  description = "Kafka service plan, e.g., business-4"
  type        = string
}

variable "service_name" {
  description = "The name of the Kafka service"
  type        = string
}

variable "kafka_version" {
  description = "The version of Kafka to use"
  type        = string
  default     = "3.7"
}

variable "public_access" {
  description = "Allow public access to the Kafka service"
  type        = bool
  default     = false
}

variable "tiered_storage_enabled" {
  description = "Enable tiered storage"
  type        = bool
  default     = false
}

variable "maintenance_window_dow" {
  description = "Day of the week for the maintenance window"
  type        = string
  default     = "sunday"
}

variable "maintenance_window_time" {
  description = "Time of the day for the maintenance window (UTC)"
  type        = string
  default     = "01:00:00"
}

variable "key_vault_id" {
  description = "The ID of the Key Vault to use for secrets"
  type        = string
}

variable "tags" {
  description = "A mapping of tags to assign to the resource"
  type        = map(string)
  default     = {}
}

variable "kafka_topics" {
  description = "Map of Kafka topics"
  type = map(object({
    topic_name             = string
    partitions             = number
    replicas               = number
    config                 = map(any)
    termination_protection = bool
  }))
  default = {
    user_actions = {
      topic_name = "user-actions"
      partitions = 3
      replicas   = 2 # Recommendation is 3 for critical topics.
      config = {
        min_insync_replicas = 1                # Recommendation is 2 for critical topics. 1, meaning only the leader needs to acknowledge the message before it is considered successfully written. leader meaning broker, which is responsible for handling all client requests (reads and writes) for a partition. replicas of the partition that are not the leader are called followers.
        cleanup_policy      = "compact,delete" # Log Compaction: Kafka ensures that the latest version of each key is retained. Log Deletion: Older log segments are still subject to deletion based on retention.ms and retention.bytes.

        retention_bytes = 104857600 # (Default -1 or unlimited) After this size is reached, the oldest segments are deleted to free up space.
        retention_ms    = 604800000 # (Default 7 days) After this time elapses, old log segments are deleted even if the size limit hasn't been reached.

        segment_bytes = 10485760 # (Default 1 GiB) Once a segment reaches this size, Kafka starts writing to a new log segment - For Aiven if segment_bytes is less than 10MiB, it will now fall back to Kafka's default value of 1GiB.
        segment_ms    = 10000    # (Default 7 days) After this time period elapses, a new log segment is created, even if the size limit hasn't been reached - For Aiven if segment_ms is less than 10 seconds, it will now fall back to Kafka's default value of 7 days.
      }
      termination_protection = false
    }
    user_actions_recovered = {
      topic_name = "user-actions-recovered"
      partitions = 3
      replicas   = 2 # Recommendation is 3 for critical topics.
      config = {
        min_insync_replicas = 1                # Recommendation is 2 for critical topics. 1, meaning only the leader needs to acknowledge the message before it is considered successfully written. leader meaning broker, which is responsible for handling all client requests (reads and writes) for a partition. replicas of the partition that are not the leader are called followers.
        cleanup_policy      = "compact,delete" # Log Compaction: Kafka ensures that the latest version of each key is retained. Log Deletion: Older log segments are still subject to deletion based on retention.ms and retention.bytes.

        retention_bytes = 104857600 # (Default -1 or unlimited) After this size is reached, the oldest segments are deleted to free up space.
        retention_ms    = 604800000 # (Default 7 days) After this time elapses, old log segments are deleted even if the size limit hasn't been reached.

        segment_bytes = 10485760 # (Default 1 GiB) Once a segment reaches this size, Kafka starts writing to a new log segment - For Aiven if segment_bytes is less than 10MiB, it will now fall back to Kafka's default value of 1GiB.
        segment_ms    = 10000    # (Default 7 days) After this time period elapses, a new log segment is created, even if the size limit hasn't been reached - For Aiven if segment_ms is less than 10 seconds, it will now fall back to Kafka's default value of 7 days.
      }
      termination_protection = false
    }
  }
}

variable "kafka_schemas" {
  description = "Map of Kafka schemas"
  type = map(object({
    file_path           = string
    subject             = string
    schema_type         = string
    compatibility_level = string
  }))
  default = {
    UserCreated = {
      file_path           = "schemas/UserCreated.avsc"
      subject             = "UserCreated"
      schema_type         = "AVRO"
      compatibility_level = "FULL_TRANSITIVE"
    },
    UserLoginAttempt = {
      file_path           = "schemas/UserLoginAttempt.avsc"
      subject             = "UserLoginAttempt"
      schema_type         = "AVRO"
      compatibility_level = "FULL_TRANSITIVE"
    },
    OrderPlaced = {
      file_path           = "schemas/OrderPlaced.avsc"
      subject             = "OrderPlaced"
      schema_type         = "AVRO"
      compatibility_level = "FULL_TRANSITIVE"
    },
    PaymentProcessed = {
      file_path           = "schemas/PaymentProcessed.avsc"
      subject             = "PaymentProcessed"
      schema_type         = "AVRO"
      compatibility_level = "FULL_TRANSITIVE"
    },
    ShipmentStatus = {
      file_path           = "schemas/ShipmentStatus.avsc"
      subject             = "ShipmentStatus"
      schema_type         = "AVRO"
      compatibility_level = "FULL_TRANSITIVE"
    },
    InventoryUpdate = {
      file_path           = "schemas/InventoryUpdate.avsc"
      subject             = "InventoryUpdate"
      schema_type         = "AVRO"
      compatibility_level = "FULL_TRANSITIVE"
    },
  }
}