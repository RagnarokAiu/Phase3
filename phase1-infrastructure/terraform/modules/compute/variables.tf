variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs"
  type        = list(string)
}

variable "app_subnet_ids" {
  description = "List of app subnet IDs"
  type        = list(string)
}

variable "app_subnet_cidrs" {
  description = "List of app subnet CIDR blocks"
  type        = list(string)
}

variable "kafka_subnet_ids" {
  description = "List of Kafka subnet IDs"
  type        = list(string)
}

variable "kafka_subnet_cidrs" {
  description = "List of Kafka subnet CIDR blocks"
  type        = list(string)
}

variable "nginx_sg_id" {
  description = "ID of Nginx security group"
  type        = string
}

variable "private_sg_id" {
  description = "ID of private app security group"
  type        = string
}

variable "kafka_sg_id" {
  description = "ID of Kafka security group"
  type        = string
}

variable "bastion_sg_id" {
  description = "ID of bastion security group"
  type        = string
}

variable "nginx_instance_type" {
  description = "Instance type for Nginx"
  type        = string
}

variable "app_instance_type" {
  description = "Instance type for app nodes"
  type        = string
}

variable "kafka_instance_type" {
  description = "Instance type for Kafka brokers"
  type        = string
}

variable "bastion_instance_type" {
  description = "Instance type for bastion host"
  type        = string
}

variable "kafka_broker_count" {
  description = "Number of Kafka brokers"
  type        = number
}

variable "zookeeper_node_count" {
  description = "Number of Zookeeper nodes"
  type        = number
}

variable "app_node_count" {
  description = "Number of app nodes"
  type        = number
  default     = 3
}

variable "alb_sg_id" {
  description = "Security group ID for ALB"
  type        = string
}

variable "service_ports" {
  description = "Port mappings for services"
  type        = map(number)
}

variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
}

variable "random_suffix" {
  description = "Random suffix for unique names"
  type        = string
}
