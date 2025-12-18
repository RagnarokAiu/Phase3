# VPC Outputs
output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.network.vpc_id
}

# Subnet Outputs
output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = module.network.public_subnet_ids
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = module.network.private_subnet_ids
}

output "app_subnet_ids" {
  description = "List of app subnet IDs"
  value       = module.network.app_subnet_ids
}

output "kafka_subnet_ids" {
  description = "List of Kafka subnet IDs"
  value       = module.network.kafka_subnet_ids
}

# Compute Outputs
output "nginx_public_ip" {
  description = "Public IP of Nginx instance"
  value       = module.compute.nginx_public_ip
}

output "bastion_public_ip" {
  description = "Public IP of bastion host"
  value       = module.compute.bastion_public_ip
}

output "kafka_bootstrap_servers" {
  description = "Kafka bootstrap servers"
  value       = module.compute.kafka_bootstrap_servers
}

# Database Outputs
output "rds_endpoints" {
  description = "Endpoints of RDS instances"
  value       = module.database.rds_endpoints
}

output "rds_ports" {
  description = "Ports of RDS instances"
  value       = module.database.rds_ports
}

# Storage Outputs
output "s3_bucket_names" {
  description = "Names of S3 buckets"
  value       = module.storage.s3_bucket_names
}