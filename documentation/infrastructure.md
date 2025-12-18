# Cloud Learning Platform - Infrastructure Documentation

## Overview
The infrastructure is built on AWS using Terraform. It follows a microservices architecture with a secure networking setup, automated CI/CD pipeline, and centralized data storage.

## Network Security

### AWS WAF & ALB
- **Load Balancer**: An **Application Load Balancer (ALB)** serves as the entry point for all traffic (HTTP/HTTPS). It routes requests to specific microservices based on URL paths.
- **Web Application Firewall (WAF)**: AWS WAF is associated with the ALB to protect against common web exploits.
    - **Managed Rules**:
        - `AWSManagedRulesCommonRuleSet`: Protection against OWASP Top 10 risks.
        - `AWSManagedRulesKnownBadInputsRuleSet`: Protection against bad inputs.
        - `AWSManagedRulesAmazonIpReputationList`: Protection against known malicious IPs.

### Security Groups
- **ALB SG**: Allows inbound HTTP (80) from anywhere (`0.0.0.0/0`).
- **App Node SG**: Allows inbound traffic ONLY from the ALB Security Group on service ports (`8000-8005`).
- **Database SG**: Allows inbound traffic only from the App Node SG.

## CI/CD Pipeline

The project uses **GitHub Actions** for Continuous Integration and Deployment.
- **Workflow**: `.github/workflows/main.yml`
- **Triggers**: Push to `main` branch.
- **Steps**:
    1. **Test**: Runs `pytest` for all backend services.
    2. **Build**: Builds Docker images for each service.
    3. **Push**: Pushes images to **AWS Elastic Container Registry (ECR)**.

## Infrastructure Components (Terraform)

### Modules
- **Network**: 
    - VPC, Public/Private Subnets across 2 AZs.
    - Internet Gateway, NAT Gateway.
    - Security Groups.
- **Compute**:
    - **ALB**: Handles routing.
    - **EC2 Instances**: Hosts the microservices (currently on App Nodes).
    - **Target Groups**: One for each service.
    - **Bastion Host**: For secure SSH access.
- **Storage**:
    - **S3 Buckets**: Stores documents, audio files, and shared assets.
- **Database**:
    - **RDS (PostgreSQL)**: Primary database for all services.

## Services & Routing
| Service | Port | Path | Description |
|---------|------|------|-------------|
| Document | 8000 | `/api/documents*` | Handles file upload and processing |
| TTS | 8001 | `/api/tts*` | Text-to-Speech conversion |
| STT | 8002 | `/api/stt*` | Speech-to-Text conversion |
| Chat | 8003 | `/api/chat*` | AI Chatbot functionality |
| Quiz | 8004 | `/api/quiz*` | Quiz generation and taking |
| User | 8005 | `/api/users*` | User authentication and profiles |
| Frontend | 80 | `/*` | React Web Application |
