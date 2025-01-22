﻿terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~> 5.0"
    }
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
  }
  backend "s3" {
    region = "us-east-1"
    bucket         = "faceless-scheduling-terraform-state-bucket"
    key            = "faceless-scheduling/state"
    dynamodb_table = "faceless-scheduling-terraform-state-locks"
    encrypt = true
  }
}

provider "aws" {
  region = "us-east-1"
}

provider "github" {
  owner = "BASIC-BIT"
  token = var.GITHUB_TOKEN
}

data "github_repository" "repo" {
  full_name = "BASIC-BIT/ScheduleBot"
}

resource "github_repository_environment" "repo_sandbox_env" {
  repository = data.github_repository.repo.name
  environment = "sandbox"
}

resource "github_actions_environment_variable" "envvar_aws_region" {
  repository = data.github_repository.repo.name
  environment = github_repository_environment.repo_sandbox_env.environment
  variable_name = "AWS_REGION"
  value = "us-east-1"
}

resource "github_actions_environment_variable" "envvar_ecr_repository" {
  repository = data.github_repository.repo.name
  environment = github_repository_environment.repo_sandbox_env.environment
  variable_name = "ECR_REPOSITORY"
  value = aws_ecr_repository.schedulebot.name
}

resource "github_actions_environment_variable" "envvar_aws_access_key_id" {
  repository = data.github_repository.repo.name
  environment = github_repository_environment.repo_sandbox_env.environment
  variable_name = "AWS_ACCESS_KEY_ID"
  value = var.AWS_TOKEN_KEY
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}


resource "aws_subnet" "subnet" {
  count = 2
  vpc_id = aws_vpc.main.id
  cidr_block = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  availability_zone = element(data.aws_availability_zones.available.names, count.index)
}

resource "aws_security_group" "ecs" {
  vpc_id = aws_vpc.main.id
  ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "rds" {
  vpc_id = aws_vpc.main.id
  ingress {
    from_port = 3306
    to_port = 3306
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "default" {
  allocated_storage = 20
  engine = "mysql"
  engine_version = "8.0.40"
  instance_class = "db.t4g.micro"
  db_name = "schedulebot"
  username = "schedulebot"
  password = var.mysql_password
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name = aws_db_subnet_group.main.name
}

resource "aws_db_subnet_group" "main" {
  name = "faceless-scheduling"
  subnet_ids = aws_subnet.subnet[*].id
}

resource "aws_ecr_repository" "schedulebot" {
  name = "schedulebot"
}

resource "aws_ecr_lifecycle_policy" "app_ecr_repo_lifecycle_policy" {
  repository = aws_ecr_repository.schedulebot.name

  policy = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Keep last two images",
            "selection": {
                "tagStatus": "any",
                "countType": "imageCountMoreThan",
                "countNumber": 2
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}

resource "aws_ecs_cluster" "main" {
  name = "faceless-scheduling"
}

resource "aws_ecs_task_definition" "main" {
  family = "schedulebot"
  network_mode = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu = "256"
  memory = "512"
  execution_role_arn = aws_iam_role.ecs_task_execution.arn
  container_definitions = jsonencode([
    {
      name = "schedulebot"
      image = "${aws_ecr_repository.schedulebot.repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = 80
          hostPort = 80
        }
      ]
      environment = [
        {
          name = "DISCORD_BOT_TOKEN"
          value = var.discord_bot_token
        },
        {
          name = "MYSQL_SERVER"
          value = aws_db_instance.default.address
        },
        {
          name = "MYSQL_DB"
          value = "schedulebot"
        },
        {
          name = "MYSQL_USER"
          value = "schedulebot"
        },
        {
          name = "MYSQL_PASSWORD"
          value = var.mysql_password
        }
      ]
    }
  ])
}

resource "aws_ecs_service" "main" {
  name = "faceless-scheduling"
  cluster = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main.arn
  desired_count = 1
  launch_type = "FARGATE"
  network_configuration {
    subnets = aws_subnet.subnet[*].id
    security_groups = [aws_security_group.ecs.id]
  }

  lifecycle {
    ignore_changes = [
      task_definition
    ]
  }

  deployment_controller {
    type = "ECS"
  }

  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent = 200
}

resource "aws_iam_role" "ecs_task_execution" {
  name = "ecs_task_execution"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_ecr" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}


data "aws_availability_zones" "available" {}