output "ecs_cluster_id" {
  value = aws_ecs_cluster.main.id
}

output "ecs_service_name" {
  value = aws_ecs_service.main.name
}

output "rds_endpoint" {
  value = aws_db_instance.default.endpoint
}

output "ecr_repository_url" {
  value = aws_ecr_repository.schedulebot.repository_url
}

output "ecs_service_url" {
  value = aws_ecs_service.main.id
}

output "db_endpoint" {
  value = aws_db_instance.default.endpoint
}

output "event_images_bucket_domain_name" {
  value = aws_s3_bucket.event_images.bucket_regional_domain_name
}

output "event_images_bucket_website_endpoint" {
  value = aws_s3_bucket_website_configuration.event_images_website.website_endpoint
}