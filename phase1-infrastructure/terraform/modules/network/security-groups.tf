# Nginx Security Group
resource "aws_security_group" "nginx" {
  name        = "${var.name_prefix}-nginx-sg"
  description = "Security group for Nginx load balancer"
  vpc_id      = aws_vpc.main.id
  
  # Allow HTTP/HTTPS from anywhere
  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # Allow SSH from anywhere (for demo - restrict in production)
  ingress {
    description = "SSH from internet"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-nginx-sg"
  })
}

# Private App Security Group
resource "aws_security_group" "private_app" {
  name        = "${var.name_prefix}-private-app-sg"
  description = "Security group for private application nodes"
  vpc_id      = aws_vpc.main.id
  
  # Allow traffic from Nginx on all service ports
  ingress {
    description     = "Service traffic from Nginx/ALB"
    from_port       = 8000
    to_port         = 8005
    protocol        = "tcp"
    security_groups = [aws_security_group.nginx.id, aws_security_group.alb.id]
  }
  
  # Allow Traffic from Bastion (SSH)
  ingress {
    description     = "SSH from Bastion"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
  }
  
  # Allow internal traffic (Kafka, service discovery)
  ingress {
    description = "Internal traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    self        = true
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-private-app-sg"
  })
}

# Kafka Security Group
resource "aws_security_group" "kafka" {
  name        = "${var.name_prefix}-kafka-sg"
  description = "Security group for Kafka cluster"
  vpc_id      = aws_vpc.main.id
  
  # Allow Kafka from app nodes
  ingress {
    description     = "Kafka from app nodes"
    from_port       = 9092
    to_port         = 9092
    protocol        = "tcp"
    security_groups = [aws_security_group.private_app.id]
  }
  
  # Allow Zookeeper from Kafka nodes
  ingress {
    description = "Zookeeper from Kafka"
    from_port   = 2181
    to_port     = 2181
    protocol    = "tcp"
    self        = true
  }
  
  # Allow inter-broker communication
  ingress {
    description = "Kafka inter-broker"
    from_port   = 9093
    to_port     = 9093
    protocol    = "tcp"
    self        = true
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-kafka-sg"
  })
}

# Database Security Group
resource "aws_security_group" "database" {
  name        = "${var.name_prefix}-database-sg"
  description = "Security group for RDS databases"
  vpc_id      = aws_vpc.main.id
  
  # Allow PostgreSQL from app nodes
  ingress {
    description     = "PostgreSQL from app nodes"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.private_app.id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-database-sg"
  })
}

# Bastion Security Group
resource "aws_security_group" "bastion" {
  name        = "${var.name_prefix}-bastion-sg"
  description = "Security group for bastion host"
  vpc_id      = aws_vpc.main.id
  
  # Allow SSH only from specific IP (configure in variables)
  ingress {
    description = "SSH from specific IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Change to your IP in production
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-bastion-sg"
  })
}

# ALB Security Group
resource "aws_security_group" "alb" {
  name        = "${var.name_prefix}-alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-alb-sg"
  })
}