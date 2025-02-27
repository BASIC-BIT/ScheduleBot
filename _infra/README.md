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
- `DOMAIN_NAME`: Domain name for the application (e.g., schedulebot.example.com)
- `CREATE_DNS_RECORD`: Set to true to enable DNS record creation
- `DNS_TTL`: Time To Live for DNS records in seconds

## Outputs

After applying the Terraform configuration, several outputs are available that can be used by the application:

- `EVENT_IMAGES_BUCKET_URL`: URL for the S3 bucket hosting event images
- `DATABASE_ENDPOINT`: Endpoint URL for the RDS database
- `ECR_REPOSITORY_URL`: URL for the ECR repository
- `ECS_CLUSTER_NAME`: Name of the ECS cluster
- `CLOUDWATCH_LOG_GROUP`: Name of the CloudWatch log group
- `ELASTIC_IP`: The Elastic IP address assigned to the application (if DNS is enabled)
- `DOMAIN_NAME`: The domain name configured for the application
- `DNS_RECORD_FQDN`: The fully qualified domain name of the DNS record

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
   DOMAIN_NAME = "schedulebot.example.com"
   CREATE_DNS_RECORD = true
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

## DNS Configuration

The infrastructure uses AWS Service Discovery to automatically map the domain `scheduling.templevr.org` to the ECS service:

1. Domain configuration:
   - Parent domain: `templevr.org`
   - Application subdomain: `scheduling.templevr.org`
   - Additional CNAME: `www.scheduling.templevr.org` (points to scheduling.templevr.org)

2. How Service Discovery works:
   - Uses your existing Route53 hosted zone for `templevr.org`
   - Registers the ECS service under the name `scheduling`
   - Automatically manages A records that point to the current IPs of your ECS tasks
   - Records are updated automatically when tasks are started, stopped, or replaced
   - No manual steps required - everything is fully automated!

3. HTTPS/SSL Support:
   - Automatically provisions an SSL certificate through AWS Certificate Manager (ACM)
   - Includes both `scheduling.templevr.org` and `www.scheduling.templevr.org` in the certificate
   - Handles DNS validation automatically
   - The ECS service is configured to accept HTTPS traffic on port 443

4. Health Checks:
   - Configures a Route53 health check for the service
   - Monitors the HTTP endpoint of the service 
   - Can be used for monitoring and alerting

5. To enable these features, the following variables are set in `terraform.tfvars`:
   ```
   DOMAIN_NAME = "scheduling.templevr.org"
   CREATE_DNS_RECORD = true
   DNS_TTL = 300
   USE_EXISTING_HOSTED_ZONE = true
   EXISTING_HOSTED_ZONE_ID = "ZXXXXXXXXXXXX"  # Your hosted zone ID
   ENABLE_HTTPS = true
   HEALTH_CHECK_PATH = "/"
   ```

6. Prerequisites:
   - You need to have the domain `templevr.org` registered and a hosted zone in Route53
   - The `EXISTING_HOSTED_ZONE_ID` must be set to your actual Route53 hosted zone ID
   - If your domain is registered elsewhere, you must have configured the name servers to point to AWS

7. DNS records created:
   - A records for `scheduling.templevr.org` pointing to your ECS service (managed automatically)
   - A CNAME record for `www.scheduling.templevr.org` pointing to `scheduling.templevr.org`
   - Validation records for SSL certificate (created during provisioning, can be removed after validation)

8. Outputs provided:
   - `SERVICE_DISCOVERY_NAMESPACE`: The namespace name (templevr.org)
   - `SERVICE_DISCOVERY_SUBDOMAIN`: The service name (scheduling)
   - `DOMAIN_NAME`: The full domain (scheduling.templevr.org)
   - `WWW_SUBDOMAIN_FQDN`: The www subdomain (www.scheduling.templevr.org)
   - `DNS_HOSTED_ZONE_ID`: The Route53 hosted zone ID
   - `SSL_CERTIFICATE_ARN`: The ARN of the SSL certificate
   - `SSL_CERTIFICATE_STATUS`: The status of the SSL certificate
   - `HEALTH_CHECK_ID`: The ID of the Route53 health check

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