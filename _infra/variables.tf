variable "DISCORD_BOT_TOKEN" {
  description = "The token of your discord bot."
  type = string
  sensitive = true
}

variable "MYSQL_PASSWORD" {
  description = "MySQL password"
  type        = string
  sensitive   = true
}

variable "GITHUB_TOKEN" {
  description = "GitHub token for CI/CD integration"
  type        = string
  sensitive   = true
}

variable "AWS_TOKEN_KEY" {
  description = "AWS token key for authentication"
  type        = string
  sensitive   = true
}

variable "AWS_REGION" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "EVENT_IMAGES_BUCKET_NAME" {
  description = "Name of the S3 bucket for event images"
  type        = string
  default     = "scheduling-assistant-event-images"
}

variable "ENVIRONMENT" {
  description = "Deployment environment"
  type        = string
  default     = "production"
} 