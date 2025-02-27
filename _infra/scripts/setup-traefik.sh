#!/bin/bash
# Simple setup script for ScheduleBot with Traefik

echo "Setting up ScheduleBot with Traefik..."

# Ensure we're in the right directory
cd "$(dirname "$0")/.." || exit 1

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    echo "Visit https://docs.docker.com/get-docker/ for installation instructions."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit https://docs.docker.com/compose/install/ for installation instructions."
    exit 1
fi

# Create the Traefik network
echo "Creating Traefik network..."
docker network create traefik-public || echo "Network already exists"

# Create the ACME file for Let's Encrypt certificates
echo "Setting up ACME file for SSL certificates..."
touch acme.json
chmod 600 acme.json

# Prompt for environment variables
read -p "Enter your domain name (e.g., example.com): " DOMAIN_NAME
read -p "Enter your Discord bot token: " DISCORD_BOT_TOKEN
read -p "Enter a MySQL root password: " MYSQL_ROOT_PASSWORD
read -p "Enter a MySQL user password: " MYSQL_PASSWORD
read -p "Enter your email address (for Let's Encrypt): " ADMIN_EMAIL
read -p "Enter a username for the Traefik dashboard: " DASHBOARD_USER
read -s -p "Enter a password for the Traefik dashboard: " DASHBOARD_PASSWORD
echo

# Create htpasswd for Traefik dashboard
HASHED_PASSWORD=$(docker run --rm httpd:2.4-alpine htpasswd -nbB "$DASHBOARD_USER" "$DASHBOARD_PASSWORD" | cut -d ":" -f 2)
TRAEFIK_DASHBOARD_AUTH="${DASHBOARD_USER}:${HASHED_PASSWORD}"

# Create .env file
cat > .env << EOL
DOMAIN_NAME=${DOMAIN_NAME}
DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN}
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
MYSQL_PASSWORD=${MYSQL_PASSWORD}
DISCORD_EVENT_ROLE_PREFIX=EventRole
ADMIN_EMAIL=${ADMIN_EMAIL}
TRAEFIK_DASHBOARD_AUTH=${TRAEFIK_DASHBOARD_AUTH}
EOL

echo ".env file created successfully."

# Start the stack
echo "Starting the ScheduleBot stack with Traefik..."
docker-compose -f docker-compose.traefik.yml up -d

echo "======================================================================================"
echo "ScheduleBot deployment with Traefik is complete!"
echo "======================================================================================"
echo "Your services are now available at:"
echo " - ScheduleBot API: https://schedulebot.${DOMAIN_NAME}"
echo " - Traefik Dashboard: https://traefik.${DOMAIN_NAME} (login with ${DASHBOARD_USER})"
echo ""
echo "Make sure your DNS records are set up to point to this server:"
echo " - schedulebot.${DOMAIN_NAME} -> [This server's IP]"
echo " - traefik.${DOMAIN_NAME} -> [This server's IP]"
echo ""
echo "You can check the status of your services with:"
echo "docker-compose -f _infra/docker-compose.traefik.yml ps"
echo ""
echo "View the logs with:"
echo "docker-compose -f _infra/docker-compose.traefik.yml logs -f"
echo "======================================================================================" 