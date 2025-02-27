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