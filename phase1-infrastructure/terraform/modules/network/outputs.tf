output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "public_subnet_cidrs" {
  description = "List of public subnet CIDR blocks"
  value       = aws_subnet.public[*].cidr_block
}

output "app_subnet_ids" {
  description = "List of app subnet IDs"
  value       = aws_subnet.private_app[*].id
}

output "app_subnet_cidrs" {
  description = "List of app subnet CIDR blocks"
  value       = aws_subnet.private_app[*].cidr_block
}

output "kafka_subnet_ids" {
  description = "List of Kafka subnet IDs"
  value       = aws_subnet.kafka[*].id
}

output "kafka_subnet_cidrs" {
  description = "List of Kafka subnet CIDR blocks"
  value       = aws_subnet.kafka[*].cidr_block
}

output "private_subnet_ids" {
  description = "List of private subnet IDs (app subnets for DB)"
  value       = aws_subnet.private_app[*].id
}

output "nginx_sg_id" {
  description = "ID of Nginx security group"
  value       = aws_security_group.nginx.id
}

output "private_sg_id" {
  description = "ID of private app security group"
  value       = aws_security_group.private_app.id
}

output "kafka_sg_id" {
  description = "ID of Kafka security group"
  value       = aws_security_group.kafka.id
}

output "db_sg_id" {
  description = "ID of database security group"
  value       = aws_security_group.database.id
}

output "bastion_sg_id" {
  description = "ID of bastion security group"
  value       = aws_security_group.bastion.id
}

output "alb_sg_id" {
  description = "ID of the ALB security group"
  value       = aws_security_group.alb.id
}
