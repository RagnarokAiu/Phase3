#!/bin/bash

# Value injected by Terraform
NODE_NUMBER=${node_number}

echo "=== Setting up App Node $${NODE_NUMBER} ==="

# Update system
apt-get update -y
apt-get upgrade -y

# Install Docker
apt-get install -y docker.io docker-compose
systemctl start docker
systemctl enable docker
usermod -aG docker ubuntu

# Create directory structure
mkdir -p /opt/cloud-platform/services
chown -R ubuntu:ubuntu /opt/cloud-platform

echo "App Node $${NODE_NUMBER} setup complete!"