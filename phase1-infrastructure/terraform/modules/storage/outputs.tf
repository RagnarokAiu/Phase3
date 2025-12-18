output "s3_bucket_names" {
  description = "Names of all S3 buckets"
  value = {
    for key, bucket in aws_s3_bucket.service_buckets :
    key => bucket.bucket
  }
}

output "s3_bucket_arns" {
  description = "ARNs of all S3 buckets"
  value = {
    for key, bucket in aws_s3_bucket.service_buckets :
    key => bucket.arn
  }
}
