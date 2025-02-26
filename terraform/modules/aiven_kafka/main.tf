locals {
  cloud_name = "azure-${var.location}"
}

# ------------------------------------------------------------------------------------------------
# Project
# ------------------------------------------------------------------------------------------------
data "aiven_project" "this" {
  project = var.project_name
}

resource "azurerm_key_vault_secret" "kafka_ca_cert" {
  name         = "kafka-ca-cert"
  value        = data.aiven_project.this.ca_cert
  key_vault_id = var.key_vault_id
}

# ------------------------------------------------------------------------------------------------
# Kafka
# ------------------------------------------------------------------------------------------------
resource "aiven_kafka" "this" {
  project                 = var.project_name
  cloud_name              = local.cloud_name
  plan                    = var.kafka_plan
  service_name            = var.service_name
  maintenance_window_dow  = var.maintenance_window_dow
  maintenance_window_time = var.maintenance_window_time

  kafka_user_config {
    kafka_version = var.kafka_version

    kafka_authentication_methods {
      certificate = false
      sasl        = true
    }

    schema_registry = true
    kafka_rest      = true
    kafka_connect   = false

    public_access {
      kafka           = var.public_access
      schema_registry = var.public_access
      kafka_rest      = var.public_access
      kafka_connect   = false
      prometheus      = false
    }

    tiered_storage {
      enabled = var.tiered_storage_enabled
    }
  }

  dynamic "tag" {
    for_each = var.tags
    content {
      key   = tag.key
      value = tag.value
    }
  }

  timeouts {
    create = "60m"
    update = "60m"
  }
}

resource "aiven_kafka_schema_configuration" "this" {
  project             = var.project_name
  service_name        = aiven_kafka.this.service_name
  compatibility_level = "FULL_TRANSITIVE"

  depends_on = [aiven_kafka.this]
}
