# Terraform Infrastructure Setup

This directory contains the Terraform configuration for deploying the ScheduleBot infrastructure to AWS.

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) (v1.0.0 or newer)
- AWS CLI configured with appropriate credentials
- S3 bucket for Terraform state (already configured in `main.tf`)

## Variables

All variables are defined in `variables.tf` and values should be provided in `terraform.tfvars`. 
Sensitive variables like `DISCORD_BOT_TOKEN` and `MYSQL_PASSWORD` should be kept secure and not committed to version control.

### Important Variables

- `AWS_REGION`: AWS region to deploy resources (default: "us-east-1")
- `EVENT_IMAGES_BUCKET_NAME`: S3 bucket name for event images
- `ENVIRONMENT`: Deployment environment (production, staging, development)
- `MYSQL_PASSWORD`: Database password (sensitive)
- `DISCORD_BOT_TOKEN`: Discord bot token (sensitive)

## Outputs

After applying the Terraform configuration, several outputs are available that can be used by the application:

- `EVENT_IMAGES_BUCKET_URL`: URL for the S3 bucket hosting event images
- `DATABASE_ENDPOINT`: Endpoint URL for the RDS database
- `ECR_REPOSITORY_URL`: URL for the ECR repository
- `ECS_CLUSTER_NAME`: Name of the ECS cluster
- `CLOUDWATCH_LOG_GROUP`: Name of the CloudWatch log group

These outputs are automatically loaded by the application using the `TerraformOutputProvider` utility.

## Deployment

1. Initialize Terraform:
   ```
   terraform init
   ```

2. Create or update `terraform.tfvars` with your specific values:
   ```
   AWS_REGION = "us-east-1"
   EVENT_IMAGES_BUCKET_NAME = "your-bucket-name"
   ENVIRONMENT = "production"
   MYSQL_PASSWORD = "your-secure-password"
   DISCORD_BOT_TOKEN = "your-discord-token"
   # Add other variables as needed
   ```

3. Preview the changes:
   ```
   terraform plan
   ```

4. Apply the changes:
   ```
   terraform apply
   ```

5. Destroy resources when no longer needed:
   ```
   terraform destroy
   ```

## Integration with Application

The application automatically loads Terraform outputs using the `TerraformOutputProvider` class.
This allows the application to dynamically configure itself based on the infrastructure that has been deployed.

The `ConfigurationService` uses the following precedence for configuration:
1. Terraform outputs
2. Configuration files (appsettings.json)
3. Environment variables
4. Default values

## AWS Resources Created

- S3 bucket for event images with public read access
- RDS MySQL database
- ECS Fargate cluster and service
- ECR repository for container images
- IAM roles and policies
- CloudWatch log group
- VPC, subnets, and security groups

## Security Considerations

- The S3 bucket for event images is configured with public read access to allow images to be accessed by users
- Database credentials are kept secure and only accessible by the application
- IAM roles follow the principle of least privilege
- Network security groups restrict access to only necessary ports 