# ScheduleBot Technical Context

## Technology Stack

### Core Framework
- **Runtime**: .NET 7.0
- **Language**: C# with nullable reference types enabled
- **Project Type**: Console application with web hosting capabilities

### Discord Integration
- **Primary Library**: DSharpPlus 4.4.2
  - `DSharpPlus.SlashCommands` - Slash command support
  - `DSharpPlus.Interactivity` - Button/modal interactions
  - `DSharpPlus.CommandsNext` - Legacy command support
  - `DSharpPlus.VoiceNext` - Voice channel capabilities (unused)
  - `DSharpPlus.Lavalink` - Audio streaming (unused)

### Database & ORM
- **Database**: MySQL 8.0.26+
- **ORM**: Entity Framework Core 7.0.8
- **Provider**: Pomelo.EntityFrameworkCore.MySql 7.0.0
- **Connection**: MySql.Data 8.0.33
- **Migration Strategy**: Code-first with automatic migrations

### Web Framework
- **API Framework**: ASP.NET Core 7.0
- **Documentation**: Swashbuckle.AspNetCore 6.5.0 (Swagger/OpenAPI)
- **Serialization**: System.Text.Json (built-in)

### Logging & Monitoring
- **Primary Logger**: Serilog 3.0.1
  - `Serilog.Sinks.Console` - Console output
  - `Serilog.Sinks.File` - File-based logging
  - `Serilog.Extensions.Logging` - .NET logging integration
  - `Serilog.Settings.Configuration` - Configuration-based setup

### Cloud Services
- **AWS SDK**: AWSSDK.S3 3.7.300.2
- **AWS Integration**: AWSSDK.Extensions.NETCore.Setup 3.7.7
- **Image Storage**: Amazon S3 with public read access

### Data Processing
- **CSV Processing**: CsvHelper 30.0.1
- **File Handling**: Built-in System.IO capabilities

## Development Setup

### Prerequisites
- **.NET 7.0 SDK**: Required for compilation and runtime
- **MySQL Server**: 8.0.26+ for database operations
- **Docker**: For containerized development and deployment
- **AWS CLI**: For infrastructure management (optional)
- **Terraform**: For infrastructure as code (optional)

### Environment Configuration
```bash
# Required Environment Variables
DISCORD_BOT_TOKEN=your_discord_bot_token
MYSQL_SERVER=localhost
MYSQL_DB=ScheduleBot
MYSQL_USER=schedulebot
MYSQL_USER_PW=your_password

# Optional Environment Variables
DISCORD_EVENT_ROLE_PREFIX=EventRole
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
AWS_REGION=us-east-1
AWS_BUCKET_NAME=your-bucket-name
```

### Development Commands
```bash
# Build and run locally
dotnet build
dotnet run

# Database migrations
dotnet ef migrations add MigrationName
dotnet ef database update

# Docker development
docker-compose up -d
docker-compose down

# Production deployment
docker build -t schedulebot .
docker push your-registry/schedulebot:latest
```

## Technical Constraints

### Discord API Limitations
- **Rate Limits**: 50 requests per second per bot
- **Message Limits**: 2000 characters per message
- **Embed Limits**: 6000 characters total, 1024 per field
- **File Upload**: 25MB limit for attachments
- **Slash Commands**: 100 global commands per application

### Database Constraints
- **Connection Pooling**: EF Core default pool size
- **Query Timeout**: 30 seconds default
- **Transaction Isolation**: Read Committed default
- **Character Set**: utf8mb4 for full Unicode support

### AWS Service Limits
- **S3 Object Size**: 5TB maximum per object
- **ECS Task Memory**: 512MB allocated
- **ECS Task CPU**: 256 CPU units (0.25 vCPU)
- **RDS Instance**: db.t4g.micro (1 vCPU, 1GB RAM)

## Dependencies Management

### Package References
```xml
<!-- Core Discord functionality -->
<PackageReference Include="DSharpPlus" Version="4.4.2" />
<PackageReference Include="DSharpPlus.SlashCommands" Version="4.4.2" />
<PackageReference Include="DSharpPlus.Interactivity" Version="4.4.2" />

<!-- Database and ORM -->
<PackageReference Include="Microsoft.EntityFrameworkCore" Version="7.0.8" />
<PackageReference Include="Pomelo.EntityFrameworkCore.MySql" Version="7.0.0" />
<PackageReference Include="MySql.Data" Version="8.0.33" />

<!-- Web API -->
<PackageReference Include="Microsoft.AspNetCore.OpenApi" Version="7.0.8" />
<PackageReference Include="Swashbuckle.AspNetCore" Version="6.5.0" />

<!-- AWS Services -->
<PackageReference Include="AWSSDK.S3" Version="3.7.300.2" />
<PackageReference Include="AWSSDK.Extensions.NETCore.Setup" Version="3.7.7" />

<!-- Logging -->
<PackageReference Include="Serilog" Version="3.0.1" />
<PackageReference Include="Serilog.Extensions.Logging" Version="7.0.0" />
<PackageReference Include="Serilog.Sinks.Console" Version="4.1.1-dev-00901" />
<PackageReference Include="Serilog.Sinks.File" Version="5.0.0" />

<!-- Utilities -->
<PackageReference Include="CsvHelper" Version="30.0.1" />
```

### Version Compatibility
- **Target Framework**: net7.0
- **C# Language Version**: 11.0 (implicit with .NET 7)
- **Nullable Reference Types**: Enabled
- **Implicit Usings**: Enabled

## Tool Usage Patterns

### Entity Framework Core
```csharp
// Database context usage pattern
using (var db = new DBEntities())
{
    var schedules = db.Schedules
        .Include(x => x.Attendees)
        .Where(x => x.ServerId == serverId)
        .ToList();
}

// Migration pattern
protected override void Up(MigrationBuilder migrationBuilder)
{
    migrationBuilder.CreateTable(
        name: "Schedules",
        columns: table => new { /* column definitions */ }
    );
}
```

### DSharpPlus Integration
```csharp
// Slash command pattern
[SlashCommand("command", "Description")]
[SlashRequireUserPermissions(Permissions.ManageMessages)]
public async Task CommandMethod(
    InteractionContext ctx,
    [Option("param", "Description")] string parameter)
{
    await ctx.CreateResponseAsync("Response");
}

// Event handling pattern
_client.ComponentInteractionCreated += OnComponentInteractionCreated;
```

### Serilog Configuration
```csharp
Log.Logger = new LoggerConfiguration()
    .WriteTo.File("Logs/schedulebot.log", rollingInterval: RollingInterval.Day)
    .WriteTo.Console()
    .MinimumLevel.Information()
    .CreateLogger();
```

## Deployment Architecture

### Docker Configuration
- **Base Image**: mcr.microsoft.com/dotnet/aspnet:7.0
- **Build Image**: mcr.microsoft.com/dotnet/sdk:7.0
- **Port Exposure**: 80 (HTTP), 443 (HTTPS)
- **Volume Mounts**: Logs directory for persistent logging

### AWS Infrastructure
- **Compute**: ECS Fargate for serverless container execution
- **Database**: RDS MySQL with automated backups
- **Storage**: S3 bucket for event images with public read access
- **Networking**: VPC with public/private subnets
- **Load Balancing**: Application Load Balancer (future)
- **DNS**: Route53 with service discovery integration

### CI/CD Pipeline
- **Source Control**: GitHub with branch protection
- **Build**: GitHub Actions with Docker build
- **Registry**: Amazon ECR for container images
- **Deployment**: Automated ECS service updates
- **Infrastructure**: Terraform state management in S3