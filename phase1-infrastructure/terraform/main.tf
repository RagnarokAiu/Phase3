# Generate random suffix for unique resource names
resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Network Module
module "network" {
  source = "./modules/network"
  
  vpc_cidr            = var.vpc_cidr
  availability_zones  = var.availability_zones
  name_prefix         = local.name_prefix
  environment         = var.environment
  common_tags         = local.common_tags
}

# Compute Module
module "compute" {
  source = "./modules/compute"
  
  depends_on = [module.network]
  
  vpc_id              = module.network.vpc_id
  public_subnet_ids   = module.network.public_subnet_ids
  app_subnet_ids      = module.network.app_subnet_ids
  app_subnet_cidrs    = module.network.app_subnet_cidrs
  kafka_subnet_ids    = module.network.kafka_subnet_ids
  kafka_subnet_cidrs  = module.network.kafka_subnet_cidrs
  
  nginx_sg_id         = module.network.nginx_sg_id
  private_sg_id       = module.network.private_sg_id
  kafka_sg_id         = module.network.kafka_sg_id
  bastion_sg_id       = module.network.bastion_sg_id
  alb_sg_id           = module.network.alb_sg_id
  
  nginx_instance_type = var.nginx_instance_type
  app_instance_type   = var.app_instance_type
  kafka_instance_type = var.kafka_instance_type
  bastion_instance_type = var.bastion_instance_type
  
  kafka_broker_count  = var.kafka_broker_count
  zookeeper_node_count = var.zookeeper_node_count
  app_node_count      = var.app_node_count
  
  service_ports       = var.service_ports
  
  name_prefix         = local.name_prefix
  environment         = var.environment
  common_tags         = local.common_tags
  
  random_suffix       = random_string.suffix.result
}

# Storage Module
module "storage" {
  source = "./modules/storage"
  
  depends_on = [module.network, module.compute]
  
  vpc_id              = module.network.vpc_id
  private_sg_id       = module.network.private_sg_id
  
  s3_buckets          = var.s3_buckets
  
  app_instance_ids    = module.compute.app_instance_ids
  kafka_instance_ids  = module.compute.kafka_instance_ids
  
  availability_zones  = var.availability_zones
  
  name_prefix         = local.name_prefix
  environment         = var.environment
  common_tags         = local.common_tags
  
  random_suffix       = random_string.suffix.result
}

# Database Module
module "database" {
  source = "./modules/database"
  
  depends_on = [module.network, module.storage]
  
  vpc_id              = module.network.vpc_id
  private_subnet_ids  = module.network.private_subnet_ids
  db_sg_id            = module.network.db_sg_id
  
  db_instance_count   = var.db_instance_count
  db_instance_class   = var.db_instance_class
  db_allocated_storage = var.db_allocated_storage
  db_username         = var.db_username
  db_password         = var.db_password
  
  name_prefix         = local.name_prefix
  environment         = var.environment
  common_tags         = local.common_tags
}

# Output values for Phase 2
output "infrastructure_outputs" {
  description = "All infrastructure outputs for Phase 2"
  value = {
    # Network
    vpc_id = module.network.vpc_id
    public_subnet_ids = module.network.public_subnet_ids
    private_subnet_ids = module.network.private_subnet_ids
    
    # Compute
    nginx_public_ip = module.compute.nginx_public_ip
    nginx_private_ip = module.compute.nginx_private_ip
    app_node_private_ips = module.compute.app_node_private_ips
    kafka_broker_ips = module.compute.kafka_broker_ips
    bastion_public_ip = module.compute.bastion_public_ip
    
    # Storage
    s3_bucket_names = module.storage.s3_bucket_names
    s3_bucket_arns = module.storage.s3_bucket_arns
    
    # Database
    rds_endpoints = module.database.rds_endpoints
    rds_ports = module.database.rds_ports
    
    # Service Configuration
    service_ports = var.service_ports
    kafka_bootstrap_servers = module.compute.kafka_bootstrap_servers
    
    # SSH Access
    ssh_key_path = module.compute.ssh_key_path
    ssh_command = "ssh -i ${module.compute.ssh_key_path} ubuntu@${module.compute.nginx_public_ip}"
  }
  sensitive = true
}