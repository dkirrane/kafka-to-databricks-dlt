# AZ CLI

```bash

# Lists Databricks workspaces in the subscription
az databricks workspace list --query '[].{name:name, resourceGroup:resourceGroup, workspaceUrl:workspaceUrl}'

# Show Databricks workspace named 'databricks-kafka-dr-poc-dbw'
az databricks workspace show --name databricks-kafka-dr-poc-dbw --resource-group databricks-kafka-dr-poc-rg --query 'workspaceUrl' -o tsv


```

# Databricks CLI

1. Create Azure Databricks configuration profile file (.databrickscfg)
   This can be generated for you using the VSCode Databricks extension

```bash
# Set host = databricks_workspace_url from Terraform output
cat ~/.databrickscfg
```

2. Useful Commands

```bash
databricks --version

# List Service Prinicpals
databricks service-principals list

databricks workspace
```

# Secret scope

```bash

#secrets/createScope

```
