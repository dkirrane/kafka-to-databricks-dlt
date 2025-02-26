# References
https://forum.confluent.io/t/databricks-spark-with-schema-registry/864


# VS Code YAML editor support
https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/work-tasks#visualstudiocode

Get the Databricks DAB yaml schema for VS Code YAML editor support
```bash
databricks bundle schema > bundle_config_schema.json
```

Add the schema to the top of the databricks.yml file
```yaml
# yaml-language-server: $schema=bundle_config_schema.json
```

In VS Code update/add the following User Settings
This will work if all the databricks DAB yaml files end with databricks.yml
```yaml
    "files.associations": {
        "*.yml": "yaml"
    },
    "yaml.schemas": {
        "file:///mnt/c/dev/GitHub/kafka_topic_dr/kafka_dr_pipeline_dab/bundle_config_schema.json": "*databricks.yml"
    }
```

# Validate

```bash
databricks bundle validate --output json
```