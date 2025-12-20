# EBS Snapshot Automation using AWS Data Lifecycle Manager

# DLM Role
resource "aws_iam_role" "dlm_lifecycle_role" {
  name = "${var.name_prefix}-dlm-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "dlm.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "dlm_lifecycle" {
  role       = aws_iam_role.dlm_lifecycle_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSDataLifecycleManagerServiceRole"
}

# EBS Backup Policy - Daily snapshots with 7-day retention
resource "aws_dlm_lifecycle_policy" "ebs_backup" {
  description        = "EBS backup policy for ${var.project_name}"
  execution_role_arn = aws_iam_role.dlm_lifecycle_role.arn
  state              = "ENABLED"

  policy_details {
    resource_types = ["VOLUME"]

    schedule {
      name = "Daily Snapshots"

      create_rule {
        interval      = 24
        interval_unit = "HOURS"
        times         = ["03:00"]  # 3 AM UTC
      }

      retain_rule {
        count = 7  # Keep 7 daily snapshots
      }

      tags_to_add = {
        SnapshotCreator = "DLM"
        Project         = var.project_name
        Environment     = var.environment
      }

      copy_tags = true
    }

    target_tags = {
      Backup = "true"
    }
  }

  tags = local.common_tags
}

# Weekly backup policy with 4-week retention for Kafka volumes
resource "aws_dlm_lifecycle_policy" "kafka_backup" {
  description        = "Weekly Kafka EBS backup policy"
  execution_role_arn = aws_iam_role.dlm_lifecycle_role.arn
  state              = "ENABLED"

  policy_details {
    resource_types = ["VOLUME"]

    schedule {
      name = "Weekly Kafka Snapshots"

      create_rule {
        interval      = 168  # 7 days in hours
        interval_unit = "HOURS"
        times         = ["02:00"]  # 2 AM UTC on Sunday
      }

      retain_rule {
        count = 4  # Keep 4 weekly snapshots
      }

      tags_to_add = {
        SnapshotCreator = "DLM-Weekly"
        Project         = var.project_name
        Type            = "Kafka"
      }

      copy_tags = true
    }

    target_tags = {
      Service = "kafka"
      Backup  = "true"
    }
  }

  tags = local.common_tags
}
