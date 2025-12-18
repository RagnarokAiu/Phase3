# Database Subnet Group (ONLY private subnets - fixed security issue)
resource "aws_db_subnet_group" "default" {
  name       = "${var.name_prefix}-db-subnet-group"
  subnet_ids = var.private_subnet_ids  # ONLY private subnets
  
  tags = {
    Name = "${var.name_prefix}-db-subnet-group"
  }
}


# Create RDS instances for each service
resource "aws_db_instance" "service_databases" {
  count = 6  # user_db, chat_db, doc_db, quiz_db, stt_db, tts_db

  identifier     = "${var.name_prefix}-db-${count.index + 1}"
  engine         = "postgres"
  # engine_version = "16.3" -> Using default
  instance_class = "db.t3.micro"
  
  allocated_storage     = 20
  storage_type         = "gp2"
  storage_encrypted    = true
  
  username = var.db_username
  password = var.db_password
  
  db_subnet_group_name   = aws_db_subnet_group.default.name
  vpc_security_group_ids = [var.db_sg_id]
  
  publicly_accessible    = false  # Critical security fix
  skip_final_snapshot    = true
  
  tags = {
    Name = "${var.name_prefix}-db-${count.index + 1}"
  }
}