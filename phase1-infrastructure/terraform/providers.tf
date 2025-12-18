terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
  
  # backend "s3" {
  #   # Configure in terraform.tfvars
  #   bucket  = "terraform-state-bucket"
  #   key     = "cloud-learning-platform/terraform.tfstate"
  #   region  = "us-east-1"
  #   encrypt = true
  # }
}

provider "aws" {
  region = var.aws_region
  
  # Use local credentials file
  shared_credentials_files = ["${path.module}/aws_credentials"]
  profile                  = var.aws_profile
}