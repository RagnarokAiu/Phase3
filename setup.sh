#!/bin/bash

echo "Setting up Cloud Learning Platform..."

# Check dependencies
echo "Checking dependencies..."
command -v docker >/dev/null 2>&1 || { echo >&2 "Docker is required but not installed. Aborting."; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo >&2 "Terraform is required but not installed. Aborting."; exit 1; }
command -v python >/dev/null 2>&1 || { echo >&2 "Python is required but not installed. Aborting."; exit 1; }

echo "Dependencies checked."

# Setup Pre-commit hooks (Optional)
# pip install pre-commit
# pre-commit install

echo "Setup complete. Please configure your .env files and terraform.tfvars before running."
