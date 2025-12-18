# Create S3 buckets for each service
resource "aws_s3_bucket" "service_buckets" {
  for_each = var.s3_buckets

  bucket = "${each.value.name_prefix}-${var.random_suffix}"
  
  tags = {
    Name    = "${var.name_prefix}-${each.key}-bucket"
    Service = each.key
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "public_access" {
  for_each = aws_s3_bucket.service_buckets

  bucket = each.value.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable versioning based on variable
resource "aws_s3_bucket_versioning" "this" {
  for_each = { for k, v in var.s3_buckets : k => v if v.versioning }

  bucket = aws_s3_bucket.service_buckets[each.key].id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Enable encryption for all buckets
resource "aws_s3_bucket_server_side_encryption_configuration" "encryption" {
  for_each = aws_s3_bucket.service_buckets

  bucket = each.value.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}