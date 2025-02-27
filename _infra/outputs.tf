# ECS outputs
output "ECS_CLUSTER_ID" {
  value = aws_ecs_cluster.main.id
  description = "The ID of the ECS cluster"
}

output "ECS_CLUSTER_NAME" {
  value = aws_ecs_cluster.main.name
  description = "The name of the ECS cluster"
}

output "ECS_SERVICE_NAME" {
  value = aws_ecs_service.main.name
  description = "The name of the ECS service"
}

output "ECS_SERVICE_ID" {
  value = aws_ecs_service.main.id
  description = "The ID of the ECS service"
}

# Database outputs
output "DATABASE_ENDPOINT" {
  value = aws_db_instance.default.address
  description = "The endpoint URL of the RDS database"
}

output "DATABASE_CONNECTION_STRING" {
  value = "Server=${aws_db_instance.default.address};Database=${aws_db_instance.default.db_name};User=${aws_db_instance.default.username};Password=${var.MYSQL_PASSWORD};"
  description = "The connection string for the MySQL database"
  sensitive = true
}

# ECR outputs
output "ECR_REPOSITORY_URL" {
  value = aws_ecr_repository.schedulebot.repository_url
  description = "The URL of the ECR repository"
}

# S3 bucket outputs
output "EVENT_IMAGES_BUCKET_URL" {
  value = "https://${aws_s3_bucket.event_images.bucket}.s3.amazonaws.com"
  description = "The URL of the S3 bucket hosting event images"
}

output "EVENT_IMAGES_BUCKET_DOMAIN_NAME" {
  value = aws_s3_bucket.event_images.bucket_regional_domain_name
  description = "The domain name of the S3 bucket hosting event images"
}

output "EVENT_IMAGES_WEBSITE_URL" {
  value = aws_s3_bucket_website_configuration.event_images_website.website_endpoint
  description = "The website URL of the S3 bucket hosting event images"
}

# CloudWatch logs output
output "CLOUDWATCH_LOG_GROUP" {
  value = aws_cloudwatch_log_group.app_log_group.name
  description = "The name of the CloudWatch log group"
}

# DNS outputs
output "SERVICE_DISCOVERY_NAMESPACE" {
  value = var.CREATE_DNS_RECORD ? (var.USE_EXISTING_HOSTED_ZONE ? data.aws_route53_zone.existing[0].name : aws_service_discovery_public_dns_namespace.templevr[0].name) : null
  description = "The Service Discovery namespace (templevr.org)"
}

output "SERVICE_DISCOVERY_SUBDOMAIN" {
  value = var.CREATE_DNS_RECORD ? aws_service_discovery_service.schedulebot[0].name : null
  description = "The Service Discovery service name (scheduling)"
}

output "DOMAIN_NAME" {
  value = var.CREATE_DNS_RECORD ? "${aws_service_discovery_service.schedulebot[0].name}.${local.parent_domain}" : null
  description = "The full domain name for the application (scheduling.templevr.org)"
}

output "WWW_SUBDOMAIN_FQDN" {
  value = var.CREATE_DNS_RECORD ? aws_route53_record.www[0].fqdn : null
  description = "The fully qualified domain name of the www subdomain (www.scheduling.templevr.org)"
}

output "DNS_HOSTED_ZONE_ID" {
  value = var.CREATE_DNS_RECORD ? local.zone_id : null
  description = "The Route53 hosted zone ID for the domain"
}

# SSL/HTTPS outputs
output "SSL_CERTIFICATE_ARN" {
  value = var.CREATE_DNS_RECORD && var.ENABLE_HTTPS ? aws_acm_certificate.scheduling_cert[0].arn : null
  description = "The ARN of the SSL certificate for HTTPS"
}

output "SSL_CERTIFICATE_STATUS" {
  value = var.CREATE_DNS_RECORD && var.ENABLE_HTTPS ? aws_acm_certificate.scheduling_cert[0].status : null
  description = "The status of the SSL certificate"
}

output "HEALTH_CHECK_ID" {
  value = var.CREATE_DNS_RECORD ? aws_route53_health_check.scheduling_health[0].id : null
  description = "The ID of the Route53 health check for the service"
}