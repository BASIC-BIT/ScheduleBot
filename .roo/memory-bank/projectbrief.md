# ScheduleBot Project Brief

## Project Overview
ScheduleBot is an open-source, self-hosted Discord event management bot designed to assist small-to-large Discord communities with event scheduling and management. The project combines Discord bot functionality with a REST API for external integrations.

## Core Purpose
- **Primary Function**: Discord-based event creation, management, and attendance tracking
- **Secondary Function**: REST API for external integrations (specifically VRChat UDON)
- **Target Users**: Discord community administrators and event organizers
- **Scale**: Small to large Discord communities (~1000 members)

## Key Requirements

### Discord Bot Features
- Event creation via slash commands with rich embeds
- Attendance tracking through Discord reactions (✅ Attending, ☑️ Tentative)
- Automatic role creation and management for events
- Thread creation for event discussions (1 hour before events)
- Event editing and deletion capabilities
- CSV import/export for bulk event management
- Administrative controls and permissions

### Web API Features
- RESTful endpoints for event data access
- Pagination and filtering capabilities
- CORS support for VRChat integration
- Future API key authentication framework
- S3 image hosting integration

### Infrastructure Requirements
- MySQL database for persistent storage
- Docker containerization
- AWS deployment (ECS, RDS, S3, ECR)
- Terraform infrastructure as code
- Continuous deployment via GitHub Actions

## Success Criteria
- Reliable event management for Discord communities
- Seamless integration with external platforms (VRChat)
- Easy deployment and maintenance
- Scalable architecture supporting growth
- Comprehensive logging and monitoring

## Technical Constraints
- Must be self-hosted
- MySQL database requirement
- Discord API limitations and rate limits
- AWS infrastructure dependencies
- .NET 7.0 framework requirement

## Current Status
- **Version**: 1.4
- **State**: Production-ready with active deployment
- **License**: MIT License
- **Repository**: BASIC-BIT/ScheduleBot