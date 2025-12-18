output "nginx_public_ip" {
  description = "Public IP of Nginx instance"
  value       = aws_instance.nginx.public_ip
}

output "nginx_private_ip" {
  description = "Private IP of Nginx instance"
  value       = aws_instance.nginx.private_ip
}

output "app_node_private_ips" {
  description = "Private IPs of app nodes"
  value       = aws_instance.app_nodes[*].private_ip
}

output "app_instance_ids" {
  description = "Instance IDs of app nodes"
  value       = aws_instance.app_nodes[*].id
}

output "kafka_broker_ips" {
  description = "Private IPs of Kafka brokers"
  value       = aws_instance.kafka_brokers[*].private_ip
}

output "kafka_instance_ids" {
  description = "Instance IDs of Kafka brokers"
  value       = aws_instance.kafka_brokers[*].id
}

output "bastion_public_ip" {
  description = "Public IP of bastion host"
  value       = aws_instance.bastion.public_ip
}

output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value       = aws_lb.main.arn
}

output "alb_dns_name" {
  description = "DNS name of the ALB"
  value       = aws_lb.main.dns_name
}

output "ssh_key_path" {
  description = "Path to SSH private key"
  value       = local_file.private_key.filename
}

output "kafka_bootstrap_servers" {
  description = "Kafka bootstrap servers"
  value       = aws_instance.kafka_brokers[*].private_ip
}
