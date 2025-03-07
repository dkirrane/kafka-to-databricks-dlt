# Overview

This repo provides a solution to integrate **Kafka** Topics with Azure **Databricks Delta Live Tables (DLT)**.
The py-spark job reads a Kafka Topic, gets the required Avro schema from Kafka Schema Registry, and deserialise the records to a Databricks Delta Live Table.

- `terraform` folder contains all the Terraform needed to provison Azure, Aiven & Databricks infrastructure.
- `kafka_topic_dr_pipeline` is the Databricks DAB (py-spark).
- `aiven_kafka` contains Python scripts to consume/produce to/from the Aiven Kafka topic using Avro for message schema & Faker for the producer.
- `scripts` folder contains scripts for working with Azure Datbricks and deploying the Databricks DAB bundle. 

## CI/CD (GitHub Actions)

#### Step 1: IaC

Run the `Terraform Apply` action to provision all the required Azure, Aiven & Databricks infrastructure.

[![Terraform Apply](https://github.com/dkirrane/kafka_topic_dr/actions/workflows/terraform-apply.yml/badge.svg)](https://github.com/dkirrane/kafka_topic_dr/actions/workflows/terraform-apply.yml)

#### Step 2: Kafka Producer

Run the `Kafka Producer` action to write some records to the a `user-actions` topic.
This is a multi-schema topic, so records have different Avro schemas.

[![Kafka Producer](https://github.com/dkirrane/kafka_topic_dr/actions/workflows/kafka-producer.yml/badge.svg)](https://github.com/dkirrane/kafka_topic_dr/actions/workflows/kafka-producer.yml)

#### Step 3: Databricks Asset Bundle (DAB)

Run the `DAB deploy` action to deploy a Databricks Asset Bundle (DAB) that contains a Delta Live Table (DLT) notebook that streams the `user-actions` topic to Databricks.

[![DAB deploy](https://github.com/dkirrane/kafka_topic_dr/actions/workflows/dab-deploy.yml/badge.svg)](https://github.com/dkirrane/kafka_topic_dr/actions/workflows/dab-deploy.yml)

#### Step 4: Verify

1. Verify the pipeline is running from the Databricks console:
   _Note it may take a few minutes for the pipeline to start as it waits for the cluster resources_

Navigate to Azure Databricks workspace > Click `Launch Workspace` > Delta Live Tables > Waiting for active compute resource... > pipline should start running
https://portal.azure.com/#@dkirrane/resource/subscriptions/XXXXXXXX/resourceGroups/databricks-kafka-dr-poc-rg/providers/Microsoft.Databricks/workspaces/databricks-kafka-dr-poc-dbw/overview

2.Check the Streaming Table
kafka_dr_pipeline > Click `user_actions` Streaming Table > click Table name > Create compute resource... > kafka_dr_pipeline (table) > Sample Data tab

#### Step 5: Cleanup

Run the `Terraform Destroy` action to delete all PoC infrastructure.

[![Terraform Destroy](https://github.com/dkirrane/kafka_topic_dr/actions/workflows/terraform-destroy.yml/badge.svg)](https://github.com/dkirrane/kafka_topic_dr/actions/workflows/terraform-destroy.yml)

## Links

#### GitHub Actions

https://github.com/dkirrane/kafka_topic_dr/actions

#### Terraform Cloud workspace

https://app.terraform.io/app/dkirrane/workspaces/databricks-kafka-dr-poc/runs
