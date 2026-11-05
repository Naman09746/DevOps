output "application_urls" {
  description = "Publicly accessible URLs for deployed container instances"
  value       = [for c in docker_container.app_replicas : "http://localhost:${c.ports[0].external}"]
}
