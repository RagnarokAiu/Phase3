resource "aws_ecr_repository" "services" {
  for_each = toset([
    "document-service",
    "tts-service",
    "stt-service",
    "chat-service",
    "quiz-service",
    "user-service",
    "frontend-web"
  ])

  name                 = "${var.project_name}-${var.environment}-${each.key}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.common_tags
}

output "ecr_repository_urls" {
  description = "URL of the ECR repositories"
  value       = { for k, v in aws_ecr_repository.services : k => v.repository_url }
}
