# AWS Configuration
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "AWS profile name"
  type        = string
  default     = "default"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name for resource tagging"
  type        = string
  default     = "cloud-learning-platform"
}

# Network Configuration
variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# Instance Configuration
variable "nginx_instance_type" {
  description = "Instance type for Nginx proxy"
  type        = string
  default     = "t3.micro"
}

variable "app_instance_type" {
  description = "Instance type for application nodes"
  type        = string
  default     = "t3.medium"
}

variable "kafka_instance_type" {
  description = "Instance type for Kafka brokers"
  type        = string
  default     = "t3.medium"
}

variable "bastion_instance_type" {
  description = "Instance type for bastion host"
  type        = string
  default     = "t2.micro"
}

# Database Configuration
variable "db_instance_count" {
  description = "Number of RDS instances to create"
  type        = number
  default     = 6
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20
}

variable "db_username" {
  description = "RDS master username"
  type        = string
  default     = "dbadmin"
  sensitive   = true
}

variable "db_password" {
  description = "RDS master password"
  type        = string
  sensitive   = true
}

# Kafka Configuration
variable "kafka_broker_count" {
  description = "Number of Kafka brokers"
  type        = number
  default     = 3
}

variable "zookeeper_node_count" {
  description = "Number of Zookeeper nodes"
  type        = number
  default     = 3
}

# Service Ports
variable "service_ports" {
  description = "Port mappings for each microservice"
  type        = map(number)
  default = {
    document = 8000
    tts      = 8001
    stt      = 8002
    chat     = 8003
    quiz     = 8004
    user     = 8005
  }
}

# S3 Buckets
variable "s3_buckets" {
  description = "S3 bucket configurations"
  type = map(object({
    name_prefix = string
    versioning  = bool
    encryption  = bool
  }))
  default = {
    document = {
      name_prefix = "document-service-storage"
      versioning  = true
      encryption  = true
    }
    tts = {
      name_prefix = "tts-service-storage"
      versioning  = false
      encryption  = true
    }
    stt = {
      name_prefix = "stt-service-storage"
      versioning  = false
      encryption  = true
    }
    chat = {
      name_prefix = "chat-service-storage"
      versioning  = true
      encryption  = true
    }
    quiz = {
      name_prefix = "quiz-service-storage"
      versioning  = true
      encryption  = true
    }
    shared = {
      name_prefix = "shared-assets"
      versioning  = true
      encryption  = true
  }
  }
}

variable "app_node_count" {
  description = "Number of application nodes"
  type        = number
  default     = 3
}