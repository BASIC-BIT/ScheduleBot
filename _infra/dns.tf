# DNS Configuration for ScheduleBot using AWS Service Discovery
# This file sets up Route53 Service Discovery to automatically map the domain to the ECS service

# Variables for DNS configuration
locals {
  # Parent domain is templevr.org
  parent_domain = "templevr.org"
  # Subdomain is scheduling.templevr.org
  subdomain_name = "scheduling"
  full_subdomain = "${local.subdomain_name}.${local.parent_domain}"
}

# Lookup the existing Route53 hosted zone for templevr.org
data "aws_route53_zone" "existing" {
  count = var.CREATE_DNS_RECORD && var.USE_EXISTING_HOSTED_ZONE ? 1 : 0
  zone_id = var.EXISTING_HOSTED_ZONE_ID != "" ? var.EXISTING_HOSTED_ZONE_ID : null
  name = var.EXISTING_HOSTED_ZONE_ID == "" ? local.parent_domain : null
  private_zone = false
}

# Create a public DNS namespace for service discovery only if not using existing zone
resource "aws_service_discovery_public_dns_namespace" "templevr" {
  count = var.CREATE_DNS_RECORD && !var.USE_EXISTING_HOSTED_ZONE ? 1 : 0
  name        = local.parent_domain
  description = "Public DNS namespace for Temple VR services"
}

# Calculate the zone ID to use (either existing or new)
locals {
  zone_id = var.CREATE_DNS_RECORD ? (
    var.USE_EXISTING_HOSTED_ZONE ? data.aws_route53_zone.existing[0].zone_id : aws_service_discovery_public_dns_namespace.templevr[0].hosted_zone_id
  ) : ""
  
  namespace_id = var.CREATE_DNS_RECORD ? (
    var.USE_EXISTING_HOSTED_ZONE ? data.aws_route53_zone.existing[0].id : aws_service_discovery_public_dns_namespace.templevr[0].id
  ) : ""
}

# Create a service discovery service for the ScheduleBot
resource "aws_service_discovery_service" "schedulebot" {
  count = var.CREATE_DNS_RECORD ? 1 : 0
  name = local.subdomain_name
  
  dns_config {
    namespace_id = local.namespace_id
    
    dns_records {
      ttl  = var.DNS_TTL
      type = "A"
    }
    
    routing_policy = "MULTIVALUE"
  }
  
  # Optional health check configuration
  health_check_custom_config {
    failure_threshold = 1
  }
}

# Create a CNAME record for www.scheduling.templevr.org
resource "aws_route53_record" "www" {
  count = var.CREATE_DNS_RECORD ? 1 : 0
  
  zone_id = local.zone_id
  name    = "www.${local.subdomain_name}"
  type    = "CNAME"
  ttl     = var.DNS_TTL
  records = ["${local.subdomain_name}.${local.parent_domain}"]
}

# Add a Route53 health check for the scheduling service
resource "aws_route53_health_check" "scheduling_health" {
  count             = var.CREATE_DNS_RECORD ? 1 : 0
  fqdn              = local.full_subdomain
  port              = 80
  type              = "HTTP"
  resource_path     = var.HEALTH_CHECK_PATH
  failure_threshold = 3
  request_interval  = 30
  
  tags = {
    Name = "scheduling-service-health-check"
    Environment = var.ENVIRONMENT
  }
}

# Create an ACM certificate for HTTPS
resource "aws_acm_certificate" "scheduling_cert" {
  count = var.CREATE_DNS_RECORD && var.ENABLE_HTTPS ? 1 : 0
  domain_name       = local.full_subdomain
  validation_method = "DNS"
  
  # Include the www subdomain in the certificate
  subject_alternative_names = ["www.${local.full_subdomain}"]
  
  lifecycle {
    create_before_destroy = true
  }
}

# Create DNS validation records for the certificate
resource "aws_route53_record" "cert_validation" {
  for_each = var.CREATE_DNS_RECORD && var.ENABLE_HTTPS ? {
    for dvo in aws_acm_certificate.scheduling_cert[0].domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  } : {}

  zone_id = local.zone_id
  name    = each.value.name
  type    = each.value.type
  ttl     = 60
  records = [each.value.record]
}

# Validate the certificate
resource "aws_acm_certificate_validation" "cert_validation" {
  count = var.CREATE_DNS_RECORD && var.ENABLE_HTTPS ? 1 : 0
  certificate_arn         = aws_acm_certificate.scheduling_cert[0].arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}

# Note: The ECS service configuration in main.tf needs to be updated to use service discovery
# This is done by adding a service_registries block to the aws_ecs_service resource 