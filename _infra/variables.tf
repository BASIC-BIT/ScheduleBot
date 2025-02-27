variable "discord_bot_token" {
  description = "The token of your discord bot."
  type = string
}

variable "mysql_password" {
  description = "MySQL password"
  type        = string
  sensitive   = true
}

variable GITHUB_TOKEN {
  sensitive = true
}
variable AWS_TOKEN_KEY {
  sensitive = true
}
variable DISCORD_CLIENT_ID {
  sensitive = true
}

variable "event_images_bucket_name" {
  description = "Name of the S3 bucket for event images"
  type        = string
  default     = "scheduling-assistant-event-images"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}