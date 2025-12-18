# Public Subnets (for Nginx, Bastion, NAT Gateways)
resource "aws_subnet" "public" {
  count = length(var.availability_zones)
  
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index + 1)  # 10.0.1.0/24, 10.0.2.0/24
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true
  
  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-public-subnet-${count.index + 1}"
    Tier = "public"
  })
}

# Private App Subnets (for Microservices)
resource "aws_subnet" "private_app" {
  count = length(var.availability_zones)
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 10)  # 10.0.10.0/24, 10.0.11.0/24
  availability_zone = var.availability_zones[count.index]
  
  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-private-app-subnet-${count.index + 1}"
    Tier = "private"
    Type = "app"
  })
}

# Kafka Subnets (for Kafka Cluster)
resource "aws_subnet" "kafka" {
  count = length(var.availability_zones)
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 20)  # 10.0.20.0/24, 10.0.21.0/24
  availability_zone = var.availability_zones[count.index]
  
  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-kafka-subnet-${count.index + 1}"
    Tier = "private"
    Type = "kafka"
  })
}