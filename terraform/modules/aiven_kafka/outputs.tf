# output "aiven_kafka" {
#   description = "dessie whole Aiven Kafka service"
#   value       = nonsensitive(jsondecode(jsonencode(aiven_kafka.this)))
#   sensitive   = false
# }

# output "kafka_service_uri" {
#   description = "URI of the created Aiven Kafka service"
#   value       = jsondecode(jsonencode(aiven_kafka.this.service_uri))
# }

output "kafka_topic_names" {
  description = "Names of the created Kafka topics"
  value       = [for topic in aiven_kafka_topic.this : topic.topic_name]
}

output "kafka_schema_names" {
  description = "Subject names of the created Kafka schemas"
  value       = [for schema in aiven_kafka_schema.this : schema.subject_name]
}
