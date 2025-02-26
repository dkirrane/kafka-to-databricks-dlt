locals {
  kafka_private = [
    for component in aiven_kafka.this.components : component
    if component.component == "kafka" && component.route == "dynamic" && component.kafka_authentication_method == "sasl"
  ]

  kafka_public = [
    for component in aiven_kafka.this.components : component
    if component.component == "kafka" && component.route == "public" && component.kafka_authentication_method == "sasl"
  ]

  schema_registry_private = [
    for component in aiven_kafka.this.components : component
    if component.component == "schema_registry" && component.route == "dynamic"
  ]

  schema_registry_public = [
    for component in aiven_kafka.this.components : component
    if component.component == "schema_registry" && component.route == "public"
  ]
}

# ------------------------------------------------------------------------------------------------
# Add Secrets to KeyVault (Private Endpoints)
# ------------------------------------------------------------------------------------------------

# Kafka (Private Endpoint)
resource "azurerm_key_vault_secret" "kafka_service_uri" {
  name         = "kafka-service-uri"
  value        = local.kafka_private[0].connection_uri
  key_vault_id = var.key_vault_id
  tags         = {}
}

# Kafka (Public Endpoint)
resource "azurerm_key_vault_secret" "kafka_service_uri_public" {
  count        = var.public_access ? 1 : 0
  name         = "kafka-service-uri-public"
  value        = local.kafka_public[0].connection_uri
  key_vault_id = var.key_vault_id
  tags         = {}
}

resource "azurerm_key_vault_secret" "kafka_admin_username" {
  name         = "kafka-admin-username"
  value        = aiven_kafka.this.service_username
  key_vault_id = var.key_vault_id
  tags         = {}
}

resource "azurerm_key_vault_secret" "kafka_admin_password" {
  name         = "kafka-admin-password"
  value        = aiven_kafka.this.service_password
  key_vault_id = var.key_vault_id
  tags         = {}
}

# Schema Registry (Private Endpoint)
resource "azurerm_key_vault_secret" "schema_registry_uri" {
  name         = "kafka-schemaregistry-uri"
  value        = "https://${aiven_kafka.this.service_username}:${aiven_kafka.this.service_password}@${local.schema_registry_private[0].connection_uri}"
  key_vault_id = var.key_vault_id
  tags         = {}
}

# Schema Registry (Public Endpoint)
resource "azurerm_key_vault_secret" "schema_registry_uri_public" {
  count        = var.public_access ? 1 : 0
  name         = "kafka-schemaregistry-uri-public"
  value        = "https://${aiven_kafka.this.service_username}:${aiven_kafka.this.service_password}@${local.schema_registry_public[0].connection_uri}"
  key_vault_id = var.key_vault_id
  tags         = {}
}
