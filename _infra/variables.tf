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

variable "DOMAIN_NAME" {
  description = "Domain name for the ScheduleBot application"
  type        = string
  default     = ""
}

variable "CREATE_DNS_RECORD" {
  description = "Whether to create DNS records for the application"
  type        = bool
  default     = false
}

variable "DNS_TTL" {
  description = "TTL (Time To Live) for DNS records in seconds"
  type        = number
  default     = 300
}

variable "USE_EXISTING_HOSTED_ZONE" {
  description = "Whether to use an existing Route53 hosted zone (set to true if domain is already registered in Route53)"
  type        = bool
  default     = true
}

variable "EXISTING_HOSTED_ZONE_ID" {
  description = "The ID of the existing Route53 hosted zone for templevr.org (only needed if USE_EXISTING_HOSTED_ZONE is true)"
  type        = string
  default     = ""
}

variable "ENABLE_HTTPS" {
  description = "Whether to enable HTTPS with an SSL certificate"
  type        = bool
  default     = true
}

variable "HEALTH_CHECK_PATH" {
  description = "The path to use for DNS health checks"
  type        = string
  default     = "/"
} 