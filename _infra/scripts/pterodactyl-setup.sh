#!/bin/bash
# Simplified Pterodactyl setup script for ScheduleBot

# Default values
PANEL_URL=${PTERODACTYL_PANEL_URL:-"https://panel.example.com"}
API_KEY=${PTERODACTYL_API_KEY:-"your-api-key"}
NODE_ID=${PTERODACTYL_NODE_ID:-1}
ALLOCATION_ID=${PTERODACTYL_ALLOCATION_ID:-1}

# Check for required commands
if ! command -v curl &> /dev/null; then
    echo "curl is required but not installed. Please install curl and try again."
    exit 1
fi

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --panel-url)
            PANEL_URL="$2"
            shift 2
            ;;
        --api-key)
            API_KEY="$2"
            shift 2
            ;;
        --node-id)
            NODE_ID="$2"
            shift 2
            ;;
        --allocation-id)
            ALLOCATION_ID="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate required parameters
if [[ -z "$PANEL_URL" || -z "$API_KEY" || -z "$NODE_ID" || -z "$ALLOCATION_ID" ]]; then
    echo "Missing required parameters. Please provide all required parameters."
    echo "Usage: $0 --panel-url URL --api-key KEY --node-id ID --allocation-id ID"
    exit 1
fi

echo "Creating ScheduleBot server in Pterodactyl..."

# Create the server
create_response=$(curl -s -X POST \
    "${PANEL_URL}/api/application/servers" \
    -H "Authorization: Bearer ${API_KEY}" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d '{
        "name": "ScheduleBot",
        "user": 1,
        "node": '${NODE_ID}',
        "allocation": {
            "default": '${ALLOCATION_ID}'
        },
        "egg": 16,
        "docker_image": "ghcr.io/pterodactyl/yolks:dotnet",
        "startup": "dotnet ScheduleBot.dll",
        "environment": {
            "DISCORD_BOT_TOKEN": "${DISCORD_BOT_TOKEN}",
            "MYSQL_PASSWORD": "${MYSQL_PASSWORD}",
            "APP_ENVIRONMENT": "production"
        },
        "limits": {
            "memory": 512,
            "swap": 0,
            "disk": 1024,
            "io": 500,
            "cpu": 100
        },
        "feature_limits": {
            "databases": 1,
            "backups": 1
        }
    }')

# Check for errors in the response
if echo "$create_response" | grep -q "errors"; then
    echo "Error creating server:"
    echo "$create_response" | jq '.errors'
    exit 1
fi

# Extract the server ID from the response
server_id=$(echo "$create_response" | jq -r '.attributes.id')

echo "Server created successfully with ID: $server_id"
echo "Server identifier: $(echo "$create_response" | jq -r '.attributes.identifier')"

# Create a webhook for automatic updates
echo "Setting up GitHub webhook for automatic updates..."

webhook_response=$(curl -s -X POST \
    "${PANEL_URL}/api/client/servers/${server_id}/webhooks" \
    -H "Authorization: Bearer ${API_KEY}" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d '{
        "name": "GitHub Auto-Update",
        "events": ["install", "reinstall"],
        "url": "https://api.github.com/repos/yourusername/ScheduleBot/dispatches",
        "content_type": "json"
    }')

# Extract the webhook token
webhook_token=$(echo "$webhook_response" | jq -r '.attributes.token')

echo "======================================================"
echo "Setup Complete!"
echo "======================================================"
echo "Server ID: $server_id"
echo "Webhook Token: $webhook_token"
echo ""
echo "Add this webhook to your GitHub repository:"
echo "URL: ${PANEL_URL}/api/client/servers/${server_id}/webhooks/${webhook_token}"
echo "Content type: application/json"
echo "Secret: <leave blank>"
echo "Events: Just the push event"
echo "======================================================" 