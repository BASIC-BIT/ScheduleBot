# ScheduleBot Active Context

## Current Work Focus

### Immediate Priority: Memory Bank Initialization
- **Status**: In Progress
- **Goal**: Establish comprehensive memory bank documentation from repository analysis
- **Context**: Fresh memory reset requires complete project understanding rebuild
- **Next Steps**: Complete remaining memory bank files (progress.md)

### Recent Changes Analysis
Based on repository analysis, the most recent significant changes include:

#### Infrastructure Enhancements
- **DNS Configuration**: Advanced Route53 service discovery setup in `_infra/dns.tf`
- **SSL/HTTPS Support**: ACM certificate provisioning with automatic validation
- **Health Checks**: Route53 health monitoring for service availability
- **Domain Management**: Support for existing hosted zones and custom domains

#### API Development
- **VRChat Integration**: REST API endpoints in [`Controllers/EventsController.cs`](Controllers/EventsController.cs:1)
- **S3 Image Service**: AWS S3 integration for event image hosting
- **CORS Configuration**: Cross-origin support for external applications
- **Authentication Framework**: Prepared API key authentication (currently disabled)

#### Service Architecture Improvements
- **ApplicationHost**: Centralized service coordination and lifecycle management
- **Service Separation**: Clean separation between Discord bot and Web API services
- **Configuration Management**: Environment-based configuration with fallbacks
- **Error Handling**: Comprehensive retry logic and graceful degradation

## Active Decisions and Considerations

### Architecture Decisions
1. **Dual Service Model**: Running both Discord bot and Web API in single container
   - **Rationale**: Simplified deployment while maintaining separation of concerns
   - **Trade-off**: Slightly higher resource usage vs. deployment complexity

2. **Database Strategy**: Direct EF Core usage without repository pattern
   - **Rationale**: EF Core provides sufficient abstraction for current needs
   - **Trade-off**: Less testability vs. reduced complexity

3. **Authentication Approach**: Prepared but disabled API key authentication
   - **Rationale**: Future-proofing while maintaining open access for initial adoption
   - **Trade-off**: Security vs. ease of integration

4. **Automation Integration**: API-first approach for external tool integration
   - **Rationale**: Enable N8n, Zapier, and other automation platforms to control events
   - **Trade-off**: Increased API surface area vs. powerful automation capabilities

### New Feature Considerations
1. **Event State Management API**: Programmatic control of event lifecycle
   - **Use Case**: External automation tools triggering event start/stop
   - **Integration**: N8n workflows, scheduled automation, external triggers

2. **Discord-VRChat Linking**: Account linking for seamless invite flow
   - **Complexity**: VRChat API integration, secure credential storage
   - **Privacy**: User consent and data protection for linked accounts

3. **Server-Specific Event APIs**: Expose Discord events per server
   - **Use Case**: External dashboards, analytics, cross-platform integration
   - **Security**: Server access validation and rate limiting

### Current Technical Debt
1. **Error Handling**: Some catch blocks are empty or too broad
2. **Testing Coverage**: Limited unit and integration tests
3. **Configuration Validation**: Missing validation for required environment variables
4. **Logging Consistency**: Mixed logging approaches across services

## Important Patterns and Preferences

### Code Organization Patterns
- **Service Layer**: All business logic encapsulated in service classes
- **Dependency Injection**: Constructor-based DI throughout application
- **Async/Await**: Consistent async patterns for all I/O operations
- **Using Statements**: Proper resource disposal with using declarations

### Discord Integration Patterns
- **Slash Commands**: Preferred over text commands for all user interactions
- **Rich Embeds**: Consistent use of DiscordEmbedBuilder for event displays
- **Permission Checks**: SlashRequireUserPermissions for administrative commands
- **Interaction Responses**: Proper response patterns for different interaction types

### Database Patterns
- **Entity Methods**: Business logic methods on entity classes (e.g., `Schedule.Update()`)
- **Transaction Management**: Explicit transactions for multi-step operations
- **Connection Management**: Using statements for DbContext lifecycle
- **Migration Strategy**: Code-first with automatic migration application

### API Design Patterns
- **RESTful Endpoints**: Standard HTTP verbs and resource-based URLs
- **Pagination**: Consistent pagination with metadata in responses
- **Error Responses**: Standardized error response format
- **CORS Support**: Configured for cross-origin requests

## Learnings and Project Insights

### Discord Bot Development
- **Rate Limiting**: Discord API rate limits require careful request management
- **Embed Limitations**: 6000 character total limit affects event description length
- **Role Management**: Automatic role creation/deletion requires careful permission handling
- **Thread Timing**: 1-hour pre-event thread creation provides optimal user engagement

### AWS Integration
- **ECS Deployment**: Fargate provides good balance of simplicity and control
- **S3 Public Access**: Requires careful bucket policy configuration for VRChat access
- **Service Discovery**: Route53 service discovery simplifies DNS management
- **Cost Optimization**: t4g.micro instances provide adequate performance for current scale

### VRChat Integration
- **UDON Limitations**: Limited HTTP request capabilities require optimized API responses
- **Image Requirements**: Public S3 URLs necessary for VRChat world image display
- **Bandwidth Considerations**: Pagination essential for large event datasets
- **CORS Requirements**: Specific CORS configuration needed for VRChat requests

### Development Workflow
- **Docker Development**: docker-compose provides consistent development environment
- **Environment Variables**: Critical for configuration management across environments
- **Migration Management**: EF Core migrations handle database schema evolution
- **CI/CD Pipeline**: GitHub Actions with ECR provides reliable deployment

## Configuration Insights

### Critical Environment Variables
```bash
# Essential for operation
DISCORD_BOT_TOKEN=required_for_discord_functionality
MYSQL_SERVER=database_host
MYSQL_USER_PW=database_password

# Important for features
AWS_BUCKET_NAME=required_for_image_hosting
AWS_REGION=affects_s3_url_generation

# Optional but recommended
DISCORD_EVENT_ROLE_PREFIX=customizes_role_naming
```

### Docker Considerations
- **Port Mapping**: 5000:80 for local development, 80 for production
- **Volume Mounts**: Logs directory for persistent logging
- **Health Checks**: MySQL health check prevents premature bot startup
- **Network Configuration**: Custom bridge network for service communication

### AWS Deployment Notes
- **ECS Task Definition**: 256 CPU units and 512MB memory sufficient for current load
- **RDS Configuration**: db.t4g.micro adequate for current database requirements
- **S3 Bucket Policy**: Public read access required for VRChat image integration
- **Security Groups**: Careful port configuration for ECS and RDS communication

## Trello Integration Status

### Current Board Structure
- **Backlog**: Tasks identified but not yet prioritized
- **On Deck**: Tasks ready to be worked on (equivalent to "Ready")
- **Doing**: Tasks currently being worked on (equivalent to "In Progress")
- **Testing**: Tasks completed but requiring validation
- **Done**: Completed and validated tasks

### Active Cards Created
Based on memory bank analysis and new automation requirements, the following cards have been created:

#### High Priority Cards
- **Implement Comprehensive Error Handling** (Backlog)
- **Complete API Key Authentication Implementation** (Backlog)
- **Implement Unit Testing Infrastructure** (Backlog)
- **API Endpoint for Event State Management** (Backlog) - NEW: Programmatic event control for N8n
- **Discord Events API Endpoint** (Backlog) - NEW: Server-specific event data exposure

#### Medium Priority Cards
- **Add Configuration Validation on Startup** (Backlog)
- **Implement Application Health Checks** (Backlog)
- **Add Recurring Events Feature** (Backlog)
- **Discord-VRChat Account Linking System** (Backlog) - NEW: Account linking with VRChat invites

#### Low Priority Cards
- **Standardize Logging Patterns** (Backlog)

### New Automation Features
Recent additions focus on external automation and cross-platform integration:
- **Event State Control**: API endpoints for starting/stopping events programmatically
- **VRChat Integration**: Discord-VRChat account linking with automatic invite functionality
- **Server Event APIs**: Expose Discord events for external tools and dashboards

### Workflow Integration
- **Task Discovery**: Query Trello for current tasks instead of maintaining lists in Memory Bank
- **Progress Tracking**: Update Trello cards as work progresses through workflow states
- **Context Updates**: Reference Trello card IDs in Memory Bank when documenting current work
- **Round-trip Updates**: Update both Memory Bank and Trello after completing work

### Current Focus
- **Memory Bank**: Completed initialization with Trello integration
- **Next Action**: Query Trello for ready tasks and begin development workflow
- **Task Management**: All detailed task tracking moved to Trello for scalability