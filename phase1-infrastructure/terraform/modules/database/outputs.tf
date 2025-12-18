output "rds_endpoints" {
  description = "Endpoints of RDS instances"
  value       = aws_db_instance.service_databases[*].address
}

output "rds_ports" {
  description = "Ports of RDS instances"
  value       = aws_db_instance.service_databases[*].port
}
