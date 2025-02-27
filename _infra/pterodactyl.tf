# Pterodactyl integration using REST API via local-exec
# Since there isn't an official Terraform provider for Pterodactyl,
# we'll use the null_resource and local-exec to interact with the API

resource "null_resource" "pterodactyl_server" {
  depends_on = [ssh_resource.setup_docker]

  # This will only run when the specified attributes change
  triggers = {
    api_key = var.PTERODACTYL_API_KEY
    app_version = "1.0.0" # Change this when you want to force recreation
  }

  # Create a server in Pterodactyl
  provisioner "local-exec" {
    command = <<-EOT
      curl -X POST \
        "${var.PTERODACTYL_PANEL_URL}/api/application/servers" \
        -H "Authorization: Bearer ${var.PTERODACTYL_API_KEY}" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d '{
          "name": "ScheduleBot",
          "user": 1,
          "egg": 16, 
          "docker_image": "ghcr.io/pterodactyl/yolks:dotnet",
          "startup": "dotnet ScheduleBot.dll",
          "environment": {
            "DISCORD_TOKEN": "${var.DISCORD_BOT_TOKEN}",
            "MYSQL_HOST": "localhost",
            "MYSQL_DATABASE": "schedulebot",
            "MYSQL_USER": "schedulebot",
            "MYSQL_PASSWORD": "${var.MYSQL_PASSWORD}",
            "APP_ENVIRONMENT": "${var.ENVIRONMENT}"
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
          },
          "allocation": {
            "default": 1
          }
        }' > pterodactyl_response.json
    EOT
  }
}

# Upload application to Pterodactyl server
resource "null_resource" "pterodactyl_app_upload" {
  depends_on = [null_resource.pterodactyl_server]
  
  triggers = {
    always_run = "${timestamp()}" # This ensures it runs every time
  }
  
  # This is a placeholder for actually uploading files to Pterodactyl
  # In a real setup, you would:
  # 1. Build your application locally or in CI
  # 2. Use SFTP or Pterodactyl API to upload files
  # 3. Restart the server
  provisioner "local-exec" {
    command = <<-EOT
      echo "Building and deploying application to Pterodactyl..."
      # Add your build and deploy steps here
      # For example:
      # - dotnet publish -c Release -o ./publish
      # - Use SFTP to upload files or Pterodactyl API to upload archive
    EOT
  }
}

# Output Pterodactyl server details
output "PTERODACTYL_SERVER_NOTE" {
  value = "Pterodactyl server setup initiated. Check the Pterodactyl panel for details."
  description = "Note about Pterodactyl server setup"
}

# Note that for a full implementation:
# 1. You'd need to extract the server ID from the API response
# 2. Handle errors properly
# 3. Implement proper state management
# 4. Set up proper file deployment workflows 