# ScheduleBot

ScheduleBot is a flexible scheduling service designed for Discord communities. It helps server administrators create, manage, and notify members about upcoming events.

## Features

- Create and manage scheduled events
- Send automatic notifications and reminders
- Customizable event roles for access control
- Web-based event calendar
- RESTful API for integration with other services
- Discord bot integration

## Deployment Options

Choose the deployment method that best fits your needs:

### 1. Pterodactyl Panel Deployment (Recommended)

The simplest way to deploy and manage ScheduleBot is using the Pterodactyl Panel, which provides a user-friendly web interface:

```bash
# Run the Pterodactyl setup script
./_infra/scripts/pterodactyl-setup.sh --panel-url https://your-panel-url --api-key your-api-key --node-id 1 --allocation-id 1
```

This script will:
- Create a new server in Pterodactyl for ScheduleBot
- Configure it with the correct environment variables
- Set up webhooks for automatic updates from GitHub

See the [Deployment Guide](./_infra/README.md) for detailed instructions on Pterodactyl setup.

### 2. Docker with Traefik (For Multiple Services)

For users who want to run multiple services with automatic SSL certificates:

```bash
# Run the Traefik setup script
./_infra/scripts/setup-traefik.sh
```

This setup leverages Traefik as a reverse proxy, providing:
- Automatic SSL certificate issuance and renewal
- Service discovery
- Load balancing
- Dashboard for monitoring

### 3. AWS Deployment (For Production at Scale)

For production deployments with scalability and high availability:

```bash
# Clone the repository
git clone https://github.com/yourusername/ScheduleBot.git
cd ScheduleBot/_infra

# Configure variables
cp terraform.tfvars.sample terraform.tfvars
nano terraform.tfvars  # Edit with your settings

# Deploy
terraform init
terraform apply
```

This will create all necessary AWS resources including ECS, RDS, S3, etc.

### 4. Development Setup

For local development:

```bash
# Clone the repository
git clone https://github.com/yourusername/ScheduleBot.git
cd ScheduleBot

# Set up the database
# ...database setup instructions...

# Run the application
dotnet run
```

## Continuous Updates from GitHub

ScheduleBot supports multiple options for staying up-to-date with the latest code:

### 1. Pterodactyl Automatic Updates (Recommended)

When using Pterodactyl Panel, updates are handled automatically:

1. During setup, a GitHub webhook is configured
2. When changes are pushed to the repository, GitHub notifies Pterodactyl
3. Pterodactyl pulls the latest changes and restarts the application
4. No additional scripts or services required

### 2. Alternative Update Methods

For non-Pterodactyl deployments, the following options are available:

#### For Docker/Traefik Deployments: Standalone Webhook

This approach runs a small webhook receiver outside Docker containers:

```bash
# On Linux/Mac
sudo ./_infra/scripts/setup-webhook-linux.sh

# On Windows (run as Administrator)
.\_infra\scripts\setup-webhook-windows.ps1
```

#### Server-side Pull with GitHub Actions

GitHub Actions can automatically deploy changes via SSH:

1. Add your server SSH credentials to GitHub repository secrets
2. GitHub will connect to your server and pull changes
3. The deployment script will update the application

#### Client-side Pull with Scheduled Tasks

Your server can periodically check for and apply updates:

```bash
# Linux/Mac (add to crontab)
0 * * * * /path/to/schedulebot/_infra/scripts/check-updates.sh >> /path/to/logs/update.log 2>&1

# Windows (PowerShell)
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File C:\schedulebot\_infra\scripts\check-updates.ps1"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "ScheduleBot Update Check"
```

## Environment Variables

ScheduleBot can be configured with the following environment variables:

- `DISCORD_BOT_TOKEN`: Your Discord bot token (required)
- `MYSQL_PASSWORD`: Database password (required)
- `ENVIRONMENT`: Deployment environment (Production, Development)
- `DISCORD_EVENT_ROLE_PREFIX`: Prefix for Discord event roles
- `GITHUB_WEBHOOK_SECRET`: Secret for validating GitHub webhooks

## Documentation

- [User Guide](./docs/user_guide.md) - How to use ScheduleBot
- [Admin Guide](./docs/admin_guide.md) - Administration and management
- [API Documentation](./docs/api.md) - RESTful API reference
- [Deployment Guide](./_infra/README.md) - Deployment options and instructions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

![ScheduleBot Logo](https://raw.githubusercontent.com/Duinrahaic/ScheduleBot/master/Resources/ScheduleBotLogo.png?token=GHSAT0AAAAAACEVC7KNJPX2H33RJJ4BMXIUZFHMXSA)

ScheduleBot is a open-source self-hosted Discord Event management bot. It's currently built to assist small-to-large discords community events.


![alt text](https://raw.githubusercontent.com/Duinrahaic/ScheduleBot/master/Resources/ScheduleBotExample.png?token=GHSAT0AAAAAACEVC7KMEWFLTWMZ56HD7NU6ZFHN4ZQ )






# Features

- Create and mange events with one-line commands
- Detailed event presentation
- Creates and remove threads for events an hour before and after the event
- Auto role management
- Attendance tracking
- Slash Commands
- Containerized! (Docker)
- AWS Deployment with Terraform

# Commands

- `Refresh` - Refreshes the UI of the schedules
- `SetEventChannel` - Sets the channel for the bot to post events
- `GetAttendanceReport` - Gets attendance report between a date range. 
- `Version` - Gets the current version of the bot
- `RestartEvent` - Restarts an event
- `Event` - Creates an event
- `Edit` - Edits an event


# How to use (Quick Start)

## Create a discord bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and give it a name.
3. Got to the bot tab and create a new bot. Write down the token. (This is your DISCORD_BOT_TOKEN)
4. Go to the general tab and copy the client ID. (This is your DISCORD_BOT_CLIENT_ID)
5. To invite you the bot to your server, go to the following link and replace the CLIENT_ID with your DISCORD_BOT_CLIENT_ID: 

           https://discord.com/oauth2/authorize?client_id=DISCORD_BOT_CLIENT_ID&scope=bot%20applications.commands&permissions=8

## Docker Deployment

This is the easiest way to get started. This will run the bot in a container. 

### Windows
1. Download and configure [Docker Desktop](https://www.docker.com/products/docker-desktop/) 
	- Windows: [Here](https://docs.docker.com/desktop/install/windows-install/)
	- Mac: [Here](https://docs.docker.com/desktop/install/mac/)
	- Linux: [Here](https://docs.docker.com/engine/install/ubuntu/)

2. Install Docker Compose
	- Windows: [Here](https://docs.docker.com/compose/install/)
	- Mac: [Here](https://docs.docker.com/compose/install/)
	- Linux: [Here](https://docs.docker.com/compose/install/)

3. (Optional) If you plan on using your own MYSQL instance to store the data, you will need to install MySQL Server. 
	- Windows: [Here](https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/windows-installation.html)
	- Mac: [Here](https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/osx-installation-pkg.html)
	- Linux: [Here](https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/linux-installation.html)
	- Docker Image: [Here](https://hub.docker.com/_/mysql)

3. Create a new folder called "Scheduling Bot" and navigate inside that folder. This is where your configuration and data will be stored.
4. Create a file called docker-compose.yaml

If you want to run the bot want to use the built-in MySQL database, your "docker-compose.yaml" file follow Option 1:

</br>

### Option 1: Using the built-in MySQL database
Your "docker-compose.yaml" file should have the following content:
```
version: '3.9'
name: schedule-bot
services:
    db:
        hostname: scheduleBot-db
        image: mysql:8.0.26
        cap_add:
            - SYS_NICE
        restart: always
        environment:
            MYSQL_DATABASE: '${MYSQL_DB}'
            MYSQL_ROOT_PASSWORD: '${MYSQL_ROOT_PW}'
            MYSQL_USER: '${MYSQL_USER}'
            MYSQL_PASSWORD: '${MYSQL_USER_PW}'
        ports:
            - '3306:3306'
        volumes:
            - db:/var/lib/mysql
            - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql
        networks:
            - scheduleBot-network
        env_file:
            - .env
        healthcheck:
            test: ["CMD", "mysqladmin", "-u {MYSQL_USER}", "-p {MYSQL_USER_PW}",  "ping", "-h", "localhost"]
            interval: 30s
            timeout: 10s
            retries: 3
    bot:
        depends_on:
            db:
                condition: service_healthy
        hostname: scheduleBot-bot
        restart: always
        environment:
            DISCORD_BOT_TOKEN: '${DISCORD_BOT_TOKEN}'
            DISCORD_EVENT_ROLE_PREFIX: '${DISCORD_EVENT_ROLE_PREFIX}'
            MYSQL_SERVER: '${MYSQL_SERVER}' # optional (Default: scheduleBot-db)
            MYSQL_DATABASE: '${MYSQL_DB}' # optional (Default: ScheduleBot)
            MYSQL_USER: '${MYSQL_USER}' # optional (Default: scheduleBot)
            MYSQL_PASSWORD: '${MYSQL_USER_PW}' # optional (Default: scheduleBot)
        image: 'duinrahaic/schedulebot:latest'
        networks:
            - scheduleBot-network
        env_file:
            - .env
volumes:
  db:
    driver: local
networks:
    scheduleBot-network:
        internal: false
        driver: bridge
        name: scheduleBot-network
```

<br>

### Optional 2: External MySQL Database

```
version: '3.9'
name: schedule-bot
services:
    bot:
        depends_on:
            db:
                condition: service_healthy
        hostname: scheduleBot-bot
        restart: always
        environment:
            DISCORD_BOT_TOKEN: '${DISCORD_BOT_TOKEN}'
            DISCORD_EVENT_ROLE_PREFIX: '${DISCORD_EVENT_ROLE_PREFIX}' # optional (Default: EventRole)
            MYSQL_SERVER: '${MYSQL_SERVER}' # optional (Default: scheduleBot-db)
            MYSQL_DATABASE: '${MYSQL_DB}' # optional (Default: ScheduleBot)
            MYSQL_USER: '${MYSQL_USER}' # optional (Default: scheduleBot)
            MYSQL_PASSWORD: '${MYSQL_USER_PW}' # optional (Default: scheduleBot)
            DISCORD_BOT_CONNECTION_STRING
        image: 'duinrahaic/schedulebot:latest'
        networks:
            - scheduleBot-network
        env_file:
            - .env
volumes:
  db:
    driver: local
networks:
    scheduleBot-network:
        internal: false
        driver: bridge
        name: scheduleBot-network
```



<br>

## Configuration:


1. In the same folder, create a file called `.env`
2. Your `.env` file should have the following content (depending on your database type):

```
#Environment Variables
#Schedule bot
DISCORD_BOT_TOKEN="YOUR_DISCORD_BOT_TOKEN_GOES_HERE" #Required
DISCORD_EVENT_ROLE_PREFIX="EventRole" #Optional
DISCORD_BOT_CONNECTION_STRING="" #Optional
#DB
MYSQL_SERVER="scheduleBot-db" #Required
MYSQL_DB="ScheduleBot" #Required
MYSQL_ROOT_PW="Password" #Required
MYSQL_USER="schedulebot" #Required
MYSQL_USER_PW="schedulebot" #Required
```

##### Notice: Change your root and user passwords to something secure. This is the password for your database. 

3. Replace `YOUR_DISCORD_BOT_TOKEN_GOES_HERE` with your Discord Bot Token from step 3 of the "Create a discord bot" section.
4. Open a command prompt and navigate to the folder you created in step 3 of the "Docker Deployment" section.
5. Run the following command: `docker-compose up -d`
6. Invite the bot to your server(s) using the link from step 5.
7. Use '/seteventchannel' and tag your event channel. This is where your bot will post about events.
8. You should now be able to use the bot in your server(s).

## Configuration Properties:

| Property Name | Description | Default Value | Optional |
| ------------- | ----------- | ------------- | -------- |
| DISCORD_BOT_TOKEN | The token of your discord bot. | | No |
| DISCORD_EVENT_ROLE_PREFIX | The prefix for the event roles. This will be used as a prefix when generating roles.| EventRole | Yes |
| DISCORD_BOT_CONNECTION_STRING | The connection string for the database. Leave blank if not in use. | | Yes |
| MYSQL_SERVER | The hostname of the MySQL server. | scheduleBot-db | No |
| MYSQL_DB | The name of the MySQL database. | ScheduleBot | No |
| MYSQL_ROOT_PW | The password of the MySQL root user. | Password | No |
| MYSQL_USER | The username of the MySQL user. | schedulebot | No |
| MYSQL_USER_PW | The password of the MySQL user. | schedulebot | No |


</br> 

### Docker Commands

- `docker-compose up -d` - Starts the bot
- `docker-compose down` - Stops the bot
- `docker logs Schedule-Bot` - Shows the logs of the bot

</br>  

## AWS Deployment with Terraform

For production deployments, you can use Terraform to deploy the bot to AWS. This will set up all the necessary infrastructure including:

- S3 bucket for event images
- RDS MySQL database
- ECS Fargate service to run the bot
- ECR repository for container images
- CloudWatch log group for monitoring

### Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) (v1.0.0 or newer)
- AWS CLI configured with appropriate credentials
- Docker installed locally for building the container image

### Deployment Steps

1. Navigate to the `_infra` directory
2. Create a `terraform.tfvars` file with your configuration:
   ```
   AWS_REGION = "us-east-1"
   EVENT_IMAGES_BUCKET_NAME = "your-bucket-name"
   ENVIRONMENT = "production"
   MYSQL_PASSWORD = "your-secure-password"
   DISCORD_BOT_TOKEN = "your-discord-token"
   # Add other variables as needed
   ```
3. Initialize Terraform:
   ```
   terraform init
   ```
4. Preview the changes:
   ```
   terraform plan
   ```
5. Apply the changes:
   ```
   terraform apply
   ```
6. After deployment, you'll see outputs with important resource information
7. The application will automatically use the deployed resources through its `TerraformOutputProvider`

For more detailed information about the Terraform setup, see the [Terraform README](./_infra/README.md).

# License 

This project is licensed under the MIT License. You can find the license [here](https://github.com/Duinrahaic/SchedulingDiscordBot/blob/98d17f5d50a274a6961871b2814ef0d4a73cf1c0/LICENSE.txt)

# Docker Hub 
Docker Image: [Here](https://hub.docker.com/r/duinrahaic/schedulebot)

`docker pull duinrahaic/schedulebot:latest`

# Techincal Support

If you need technical support with this project create an issue.

# Donation Support

If you would like to support this project, you can do so via donations [here](https://ko-fi.com/duinrahaic)

If you want to support me long term you can subscribe to my [Patreon](https://www.patreon.com/duinrahaic)

# Contributing

If you would like to contribute to this project, please create a pull request. If you have any questions, please create an issue.

# Credits

- [dsharpplus.net](https://dsharpplus.net/) - Discord API Wrapper
- [Logo](https://twitter.com/Wishes_4_Fishes/) - Logo Designer
