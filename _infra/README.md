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

# ScheduleBot Deployment Guide

This directory contains infrastructure and deployment configurations for the ScheduleBot application.

## Deployment Options

ScheduleBot now supports three primary deployment methods:

### 1. Pterodactyl Panel (Recommended for Simple Setup)

Pterodactyl is a game server management panel that can be used to easily deploy and manage ScheduleBot.

#### Setting up Pterodactyl:

1. Set up a Pterodactyl panel and node following the [official documentation](https://pterodactyl.io)
2. Run the setup script:

```bash
./_infra/scripts/pterodactyl-setup.sh --panel-url https://your-panel-url --api-key your-api-key --node-id 1 --allocation-id 1
```

This will:
- Create a new server in Pterodactyl for ScheduleBot
- Configure it with the correct environment variables
- Set up webhooks for automatic updates

#### Benefits of Pterodactyl:
- User-friendly web interface for management
- Built-in file management
- Console access
- Resource monitoring
- Automatic backups
- Simple start/stop/restart controls

### 2. Docker with Traefik (Recommended for Multiple Services)

For users who want to run multiple services with automatic SSL:

```bash
# Run the setup script
./_infra/scripts/setup-traefik.sh
```

Alternatively, you can manually set up the environment:

```bash
# Create the Traefik network
docker network create traefik-public

# Create the ACME file for Let's Encrypt certificates
touch _infra/acme.json
chmod 600 _infra/acme.json

# Start the stack
docker-compose -f _infra/docker-compose.traefik.yml up -d
```

This setup leverages Traefik as a reverse proxy, providing:
- Automatic SSL certificate issuance and renewal
- Service discovery
- Load balancing
- Dashboard for monitoring

### 3. AWS Deployment (For Production at Scale)

For production deployments with scalability and high availability:

```bash
cd _infra
cp terraform.tfvars.sample terraform.tfvars
# Edit terraform.tfvars with your settings
terraform init
terraform apply
```

This will create all necessary AWS resources including ECS, RDS, S3, etc.

## Automatic Updates

Each deployment method supports automatic updates:

### Pterodactyl Updates (Recommended)
- GitHub pushes trigger Pterodactyl's webhook
- Pterodactyl automatically pulls changes and restarts the service
- No custom scripts or services needed

### Docker/Traefik Updates
Two options are available:

1. **Using the Standalone Webhook Receiver** (Recommended for Docker)
```bash
# On Linux
sudo ./_infra/scripts/setup-webhook-linux.sh

# On Windows (run as Administrator)
.\_infra\scripts\setup-webhook-windows.ps1
```

2. **Using GitHub Actions**
- GitHub Actions workflow builds and pushes new Docker images
- Optional Watchtower container automatically updates running containers

### AWS Updates
- GitHub Actions workflow triggers ECS deployments
- Blue/green deployments ensure zero downtime

## Configuration

Environment variables for all deployment methods:

- `DISCORD_BOT_TOKEN`: Your Discord bot token (required)
- `MYSQL_PASSWORD`: Database password (required)
- `ENVIRONMENT`: Deployment environment (Production, Development)
- `DISCORD_EVENT_ROLE_PREFIX`: Prefix for Discord event roles
- `GITHUB_WEBHOOK_SECRET`: Secret for validating GitHub webhooks (for webhook updates)

## Getting Help

If you encounter issues with deployment:
1. Check the logs in your chosen deployment platform
2. Refer to the appropriate documentation for your deployment method
3. Open an issue on GitHub for further assistance

## Directory Structure

- `_infra/` - Infrastructure and deployment files
  - `scripts/` - Deployment and utility scripts
    - `pterodactyl-setup.sh` - Script to set up ScheduleBot on Pterodactyl
    - `setup-traefik.sh` - Script to set up ScheduleBot with Traefik
    - `setup-webhook-linux.sh` - Script to set up webhook receiver on Linux
    - `setup-webhook-windows.ps1` - Script to set up webhook receiver on Windows
    - `check-updates.ps1` - PowerShell script for checking and applying updates
    - `check-updates.sh` - Bash script for checking and applying updates
  - `docker-compose.traefik.yml` - Docker Compose file for Traefik deployment
  - `traefik.yml` - Configuration file for Traefik
  - `backups/` - Database backups directory (created automatically)

## Deployment Methods

There are three main ways to deploy and manage the ScheduleBot application:

### 1. Manual Deployment

Use the provided deployment scripts to manually deploy, update, and manage the application:

#### For Linux/Mac users:

```bash
# Deploy from scratch
./_infra/deploy.sh deploy

# Update the application
./_infra/deploy.sh update

# Stop the application
./_infra/deploy.sh stop

# Backup the database
./_infra/deploy.sh backup
```

#### For Windows users:

```powershell
# Deploy from scratch
.\_infra\deploy.ps1 deploy

# Update the application
.\_infra\deploy.ps1 update

# Stop the application
.\_infra\deploy.ps1 stop

# Backup the database
.\_infra\deploy.ps1 backup
```

### 2. Automatic Updates from GitHub

The application can automatically update itself when changes are pushed to the main branch on GitHub.

#### Using GitHub Webhooks (Recommended)

The most efficient method for automatic updates is to use GitHub webhooks. This approach allows GitHub to notify your server directly when changes are pushed to the repository.

#### Option 1: Standalone Webhook Receiver (Recommended for Docker deployments)

For Docker deployments, the best approach is to use the standalone Node.js webhook receiver that runs directly on the host machine:

**Setup on Linux/Mac:**

```bash
# Install and configure the webhook receiver
sudo ./_infra/scripts/setup-webhook-linux.sh
```

**Setup on Windows:**

```powershell
# Run as Administrator
.\_infra\scripts\setup-webhook-windows.ps1
```

These scripts will:
1. Check for and install Node.js if needed
2. Set up the webhook receiver as a system service
3. Configure it to start automatically on boot
4. Open the necessary firewall port

**How it works:**
- The webhook receiver runs outside the Docker container on the host
- When GitHub sends a webhook, the receiver verifies it and runs the appropriate deploy script
- The deploy script pulls the latest code and updates the Docker containers
- This approach solves the container isolation problem

#### Option 2: API Webhook (For non-Docker deployments)

If you're not using Docker, you can use the built-in webhook endpoint in the application's API:

**Setup Instructions:**

1. **In your GitHub repository:**
   - Go to Settings → Webhooks → Add webhook
   - Set Payload URL to: `https://yourdomain.com/api/webhook/github`
   - Content type: `application/json`
   - Secret: Create a strong random string
   - Events: Select "Just the push event"
   - Enable SSL verification
   - Click "Add webhook"

2. **On your server:**
   - Add these environment variables:
     ```
     GITHUB_WEBHOOK_SECRET=your-webhook-secret
     APP_DIR=/path/to/your/application  # Or C:\path\to\your\application on Windows
     BRANCH=main  # or whatever branch you want to monitor
     ```

### Using GitHub Actions (Server-side Pull)

The GitHub Actions workflow (`.github/workflows/deploy.yml`) is triggered when changes are pushed to the main branch. It connects to your server via SSH and runs the update script.

**Requirements:**

1. Set up the following GitHub secrets in your repository settings:
   - `VPS_HOST`: Your server's hostname or IP address
   - `VPS_USERNAME`: SSH username
   - `VPS_PORT`: SSH port (usually 22)
   - `SSH_PRIVATE_KEY`: Your SSH private key for authentication
   - `APP_DIRECTORY`: Path to the application directory on your server

### Using a Scheduled Task (Client-side Pull)

For servers that cannot accept incoming connections (webhooks or SSH), you can set up a scheduled task on the server to periodically check for updates.

**For Windows servers:**

1. Save the application in a known location (e.g., `C:\schedulebot`)
2. Create a scheduled task to run the update script periodically:

```powershell
# Create a scheduled task that runs every hour
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File C:\schedulebot\_infra\scripts\check-updates.ps1"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 60)
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "ScheduleBot Update Check" -Description "Checks for ScheduleBot updates from GitHub"
```

**For Linux/Mac servers:**

1. Add a cron job to run the update script periodically:

```bash
# Add to crontab to run every hour
0 * * * * /path/to/schedulebot/_infra/scripts/check-updates.sh >> /path/to/schedulebot/_infra/logs/cron.log 2>&1
```

## Configuration

The deployment scripts support several environment variables for customization:

- `APP_DIR`: Application directory path
- `BRANCH`: Git branch to track (default: `main`)
- `REMOTE`: Git remote to pull from (default: `origin`)
- `COMPOSE_FILE`: Docker Compose file (default: `docker-compose.yml`)
- `ENV_FILE`: Environment file (default: `.env`)
- `GITHUB_WEBHOOK_SECRET`: Secret for validating GitHub webhooks

## Troubleshooting

### Common Issues

1. **Pterodactyl Setup Issues**
   - Check that your API key has the correct permissions
   - Ensure your node has available resources
   - Verify the allocation is not in use

2. **Docker Container Issues**
   - Check container logs: `docker-compose logs -f`
   - Ensure ports aren't in use by other services

3. **Update Problems**
   - Verify your git repository is clean: `git status`
   - Check if there are merge conflicts
   - Ensure deploy scripts have execute permissions: `chmod +x _infra/deploy.sh`

4. **Database Issues**
   - Check database connection string
   - Verify database service is running

### Webhook Issues

1. **Failed Webhooks**
   - Check GitHub webhook delivery logs in repository settings
   - Ensure your server is publicly accessible
   - Verify `GITHUB_WEBHOOK_SECRET` matches what you set in GitHub
   - Check application logs for webhook processing errors

### Logs

- Pterodactyl logs: Available in the Pterodactyl panel console
- Docker logs: `docker-compose -f _infra/docker-compose.traefik.yml logs -f`
- Webhook logs: Check your application's standard logging output
- Update logs: `/opt/schedulebot/_infra/logs/update.log`

For more help, please open an issue on the GitHub repository. 