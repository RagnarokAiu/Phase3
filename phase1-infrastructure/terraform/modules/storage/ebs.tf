# EBS Volumes for Kafka (high performance storage)
resource "aws_ebs_volume" "kafka_data" {
  count = length(var.kafka_instance_ids)

  availability_zone = element(var.availability_zones, count.index)
  size              = 100  # GB
  type              = "gp3"
  encrypted         = true

  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-kafka-data-${count.index + 1}"
  })
}

# Attach EBS volumes to Kafka instances
resource "aws_volume_attachment" "kafka_ebs_attach" {
  count = length(var.kafka_instance_ids)

  device_name = "/dev/sdf"
  volume_id   = aws_ebs_volume.kafka_data[count.index].id
  instance_id = var.kafka_instance_ids[count.index]
}

# EBS Volumes for app nodes
resource "aws_ebs_volume" "app_data" {
  count = length(var.app_instance_ids)

  availability_zone = element(var.availability_zones, count.index % length(var.availability_zones))
  size              = 50  # GB
  type              = "gp3"
  encrypted         = true

  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-app-data-${count.index + 1}"
  })
}

# Attach EBS volumes to app nodes
resource "aws_volume_attachment" "app_ebs_attach" {
  count = length(var.app_instance_ids)

  device_name = "/dev/sdf"
  volume_id   = aws_ebs_volume.app_data[count.index].id
  instance_id = var.app_instance_ids[count.index]
}