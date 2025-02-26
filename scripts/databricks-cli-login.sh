#!/bin/bash
set -e

#
# Databricks CLI login
# https://learn.microsoft.com/en-us/azure/databricks/dev-tools/cli/tutorial
#

# 1. Install databricks CLI

# 2. Authenticate with Databricks
# az login

# 3. Create Azure Databricks configuration profile (code ~/.databrickscfg)
CONFIG_FILE="$HOME/.databrickscfg"
if [ -f "$CONFIG_FILE" ]; then
    echo "$CONFIG_FILE already exists. Backing up the old config."
    mv "$CONFIG_FILE" "$CONFIG_FILE.bak"
fi

DBW_URL=$( az databricks workspace show --name databricks-kafka-dr-poc-dbw --resource-group databricks-kafka-dr-poc-rg --query 'workspaceUrl' -o tsv )

cat <<EOL > "$CONFIG_FILE"
[DEFAULT]
host = ${DBW_URL}
auth_type = azure-cli
EOL

# 4. Validate the connection
databricks auth profiles
databricks auth env --profile DEFAULT
databricks clusters list --profile DEFAULT
