# Key Pair for SSH access
resource "tls_private_key" "key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "deployer" {
  key_name   = "${var.name_prefix}-key"
  public_key = tls_private_key.key.public_key_openssh
  
  tags = var.common_tags
}

resource "local_file" "private_key" {
  filename        = "${path.module}/../../../${var.name_prefix}-key.pem"
  content         = tls_private_key.key.private_key_pem
  file_permission = "0400"
}
