output "cluster_id" {
  description = "The ID of the created Databricks cluster"
  value       = databricks_cluster.this.id
}

output "cluster_url" {
  description = "The URL of the created Databricks cluster"
  value       = databricks_cluster.this.url
}