# S3 bucket for event images
resource "aws_s3_bucket" "event_images" {
  bucket = var.event_images_bucket_name
  
  tags = {
    Name        = "Event Images"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_website_configuration" "event_images_website" {
  bucket = aws_s3_bucket.event_images.id
  
  index_document {
    suffix = "index.html"
  }
}

resource "aws_s3_bucket_public_access_block" "event_images_access" {
  bucket = aws_s3_bucket.event_images.id
  
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "allow_public_read" {
  bucket = aws_s3_bucket.event_images.id
  policy = data.aws_iam_policy_document.allow_public_read.json
}

data "aws_iam_policy_document" "allow_public_read" {
  statement {
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    
    actions = [
      "s3:GetObject"
    ]
    
    resources = [
      "${aws_s3_bucket.event_images.arn}/*"
    ]
  }
}

resource "aws_s3_bucket_cors_configuration" "event_images_cors" {
  bucket = aws_s3_bucket.event_images.id
  
  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
} 