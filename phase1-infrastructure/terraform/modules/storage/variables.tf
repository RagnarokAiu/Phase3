variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
}

variable "private_sg_id" {
  description = "ID of private app security group"
  type        = string
}

variable "s3_buckets" {
  description = "S3 bucket configurations"
  type = map(object({
    name_prefix = string
    versioning  = bool
    encryption  = bool
  }))
}

variable "app_instance_ids" {
  description = "List of app instance IDs for EBS attachment"
  type        = list(string)
}

variable "kafka_instance_ids" {
  description = "List of Kafka instance IDs for EBS attachment"
  type        = list(string)
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
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
