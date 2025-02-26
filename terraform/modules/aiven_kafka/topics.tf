
# ------------------------------------------------------------------------------------------------
# Create Kafka topics
# ------------------------------------------------------------------------------------------------
# https://registry.terraform.io/providers/aiven/aiven/latest/docs/resources/kafka_topic
resource "aiven_kafka_topic" "this" {
  for_each = var.kafka_topics

  project      = var.project_name
  service_name = aiven_kafka.this.service_name

  topic_name  = each.value.topic_name
  partitions  = each.value.partitions
  replication = each.value.replicas

  config {
    min_insync_replicas = lookup(each.value.config, "min_insync_replicas", null)
    cleanup_policy      = lookup(each.value.config, "cleanup_policy", null)

    retention_ms    = lookup(each.value.config, "retention_ms", null)
    retention_bytes = lookup(each.value.config, "retention_bytes", null)

    segment_ms    = lookup(each.value.config, "segment_ms", null)
    segment_bytes = lookup(each.value.config, "segment_bytes", null)

    # Tiered Storage - https://aiven.io/docs/products/kafka/howto/configure-topic-tiered-storage
    # By default, local_retention_bytes and local_retention_ms are set to -2
    remote_storage_enable = var.tiered_storage_enabled
    local_retention_ms    = -2
    local_retention_bytes = -2
  }

  termination_protection = each.value.termination_protection

  timeouts {
    create = "60m"
    update = "60m"
  }
}


# ------------------------------------------------------------------------------------------------
# Create Schemas in Schema Registry
# ------------------------------------------------------------------------------------------------
# https://registry.terraform.io/providers/aiven/aiven/latest/docs/resources/kafka_schema
resource "aiven_kafka_schema" "this" {
  for_each = var.kafka_schemas

  project      = var.project_name
  service_name = aiven_kafka.this.service_name

  schema              = file("${path.module}/${each.value.file_path}")
  subject_name        = each.value.subject
  schema_type         = each.value.schema_type
  compatibility_level = each.value.compatibility_level

  timeouts {
    create = "60m"
    update = "60m"
  }
}