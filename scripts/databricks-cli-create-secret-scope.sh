#!/bin/bash
set -e

#
# Databricks create KeyVault-backed secret scope
# https://learn.microsoft.com/en-us/azure/databricks/security/secrets/secret-scopes#create-an-azure-key-vault-backed-secret-scope-1
#
# BEFORE RUNNING THIS SCRIPT RUN: ./databricks-cli-login.sh

# Get Azure KeyVault details
AZURE_KEYVAULT_NAME="databricks-kafka-dr-poc-kv"
AZURE_KEYVAULT_ID=$(az keyvault show --name ${AZURE_KEYVAULT_NAME} --query id -o tsv)
AZURE_KEYVAULT_URI=$(az keyvault show --name ${AZURE_KEYVAULT_NAME} --query properties.vaultUri -o tsv)

# Create Databricks (Azure Key Vault-backed) secret scope

SECRET_SCOPE_NAME="keyvault_secrets"

json_payload=$(
    cat <<EOF
{
   "scope":"$SECRET_SCOPE_NAME",
   "initial_manage_principal":"users",
   "scope_backend_type":"AZURE_KEYVAULT",
   "backend_azure_keyvault":{
      "dns_name":"$AZURE_KEYVAULT_URI",
      "resource_id":"$AZURE_KEYVAULT_ID"
   }
}
EOF
)

# Check if the secret scope already exists use json output and use jq to get name matches ${SECRET_SCOPE_NAME}
exists=$( databricks secrets list-scopes --output json | jq -e '.[]? | select(.name == "'"${SECRET_SCOPE_NAME}"'") | length > 0' > /dev/null && echo "true" || echo "false" )
if [ "${exists}" == "true" ]; then
    echo -e "\nSecret scope ${SECRET_SCOPE_NAME} already exists. Skipping creation."
else
    echo -e "\nSecret scope ${SECRET_SCOPE_NAME} does not exist. Creating..."

    # Create the secret scope
    echo -e "\nCreating secret scope ${SECRET_SCOPE_NAME}..."
    databricks secrets create-scope --json "${json_payload}" --profile DEFAULT
fi

# List all secret scopes
echo -e "\nListing all secret scopes..."
databricks secrets list-scopes --profile DEFAULT

# List the ACLs for the secret scope
echo -e "\nListing ACLs for secret scope ${SECRET_SCOPE_NAME}..."
databricks secrets list-acls ${SECRET_SCOPE_NAME} --profile DEFAULT

# Lists the secret keys that are stored at this scope
echo -e "\nListing secret keys for secret scope ${SECRET_SCOPE_NAME}..."
databricks secrets list-secrets ${SECRET_SCOPE_NAME} --profile DEFAULT
