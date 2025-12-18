# Key Pair (moved to key-pair.tf)

locals {
  kafka_ips = [
    for i in range(var.kafka_broker_count) : 
    cidrhost(
      var.kafka_subnet_cidrs[i % length(var.kafka_subnet_cidrs)], 
      10 + i
    )
  ]
}

# Latest Ubuntu AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical
  
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
  
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Nginx Load Balancer
resource "aws_instance" "nginx" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.nginx_instance_type
  subnet_id              = var.public_subnet_ids[0]
  vpc_security_group_ids = [var.nginx_sg_id]
  key_name               = aws_key_pair.deployer.key_name
  
  associate_public_ip_address = true
  
  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }
  
  user_data = templatefile("${path.module}/user-data/nginx-setup.sh", {
    app_node_ips = [
      for i in range(var.app_node_count) : 
      cidrhost(
        var.app_subnet_cidrs[i % length(var.app_subnet_cidrs)], 
        10 + i
      )
    ]
    service_ports = var.service_ports
  })
  
  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-nginx"
    Role = "load-balancer"
  })
}

# App Nodes (3 nodes for high availability)
resource "aws_instance" "app_nodes" {
  count = var.app_node_count
  
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.app_instance_type
  subnet_id              = var.app_subnet_ids[count.index % length(var.app_subnet_ids)]
  vpc_security_group_ids = [var.private_sg_id]
  key_name               = aws_key_pair.deployer.key_name
  
  private_ip = cidrhost(
    var.app_subnet_cidrs[count.index % length(var.app_subnet_cidrs)], 
    10 + count.index
  )
  
  root_block_device {
    volume_size = 50
    volume_type = "gp3"
    encrypted   = true
  }
  
  user_data = templatefile("${path.module}/user-data/app-setup.sh", {
    node_number     = count.index + 1
    service_ports   = var.service_ports
    random_suffix   = var.random_suffix
  })
  
  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-app-node-${count.index + 1}"
    Role = "microservices"
    Node = count.index + 1
  })
}

# Kafka Brokers
resource "aws_instance" "kafka_brokers" {
  count = var.kafka_broker_count
  
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.kafka_instance_type
  subnet_id              = var.kafka_subnet_ids[count.index % length(var.kafka_subnet_ids)]
  vpc_security_group_ids = [var.kafka_sg_id]
  key_name               = aws_key_pair.deployer.key_name
  
  private_ip = cidrhost(
    var.kafka_subnet_cidrs[count.index % length(var.kafka_subnet_cidrs)], 
    10 + count.index
  )
  
  root_block_device {
    volume_size = 100
    volume_type = "gp3"
    encrypted   = true
  }


  user_data = templatefile("${path.module}/user-data/kafka-setup.sh", {
    broker_id     = count.index + 1
    broker_count  = var.kafka_broker_count
    broker_ips    = local.kafka_ips
    random_suffix = var.random_suffix
  })
  
  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-kafka-broker-${count.index + 1}"
    Role = "kafka"
    BrokerID = count.index + 1
  })
}

# Bastion Host
resource "aws_instance" "bastion" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.bastion_instance_type
  subnet_id              = var.public_subnet_ids[0]
  vpc_security_group_ids = [var.bastion_sg_id]
  key_name               = aws_key_pair.deployer.key_name
  
  associate_public_ip_address = true
  
  root_block_device {
    volume_size = 10
    volume_type = "gp3"
  }
  
  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-bastion"
    Role = "bastion"
  })
}