terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "4.3.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "3.0.1"
    }
    databricks = {
      source  = "databricks/databricks"
      version = "1.52.0"
    }
    aiven = {
      source  = "aiven/aiven"
      version = "4.26.0"
    }
  }

  backend "remote" {
    hostname     = "app.terraform.io"
    organization = "dkirrane"

    workspaces {
      name = "databricks-kafka-dr-poc"
    }
  }
}

# https://www.terraform.io/docs/providers/azurerm/index.html
provider "azurerm" {
  features {}
}

# https://registry.terraform.io/providers/hashicorp/azuread/latest/docs/
provider "azuread" {
}

# https://registry.terraform.io/providers/aiven/aiven/latest/docs
provider "aiven" {
}

# https://registry.terraform.io/providers/databricks/databricks/latest/docs#special-configurations-for-azure
provider "databricks" {
  host                        = var.databricks_workspace_enabled ? module.databricks_workspace[0].workspace_url : null
  azure_workspace_resource_id = var.databricks_workspace_enabled ? module.databricks_workspace[0].workspace_id : null
}