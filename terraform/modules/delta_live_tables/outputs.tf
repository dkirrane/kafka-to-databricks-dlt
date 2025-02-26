output "pipeline_id" {
  description = "The ID of the created Delta Live Table pipeline"
  value       = databricks_pipeline.this.id
}

output "pipeline_url" {
  description = "The URL of the created Delta Live Table pipeline"
  value       = databricks_pipeline.this.url
}

# output "notebook_url" {
#   description = "The URL of the created DLT notebook"
#   value       = databricks_notebook.dlt_notebook.url
# }