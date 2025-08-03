# ScheduleBot System Patterns

## System Architecture

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Discord API   │    │   REST API      │    │   External      │
│   (DSharpPlus)  │    │   (ASP.NET)     │    │   Clients       │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴───────────┐
                    │   ApplicationHost       │
                    │   (Service Coordinator) │
                    └─────────────┬───────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
┌───────▼───────┐    ┌────────────▼────────────┐    ┌───────▼───────┐
│ DiscordBot     │    │    DatabaseService      │    │   WebAPI      │
│ Service        │    │    (EF Core/MySQL)      │    │   Service     │
└────────────────┘    └─────────────────────────┘    └───────────────┘
```

### Service-Oriented Design
- **ApplicationHost**: Central coordinator managing service lifecycle
- **Service Isolation**: Each major function encapsulated in dedicated services
- **Dependency Injection**: Constructor-based DI with ServiceProvider
- **Configuration Management**: Centralized configuration through IConfigurationService

## Key Technical Decisions

### Database Strategy
- **ORM Choice**: Entity Framework Core for type safety and migrations
- **Database**: MySQL for reliability and community support
- **Migration Strategy**: Code-first with automatic migration application
- **Connection Management**: Environment variable-based configuration

### Discord Integration Patterns
- **Command Pattern**: Slash commands with attribute-based routing
- **Event-Driven Architecture**: Discord events trigger business logic
- **Interaction Handling**: Separate handlers for different interaction types
- **State Management**: Database persistence for all stateful operations

### API Design Patterns
- **RESTful Design**: Standard HTTP verbs and status codes
- **Pagination**: Cursor-based pagination for large datasets
- **Filtering**: Query parameter-based filtering
- **CORS Support**: Configured for VRChat and external integrations

## Design Patterns in Use

### Service Layer Pattern
```csharp
public interface IDiscordBotService
{
    Task StartAsync();
}

public class DiscordBotService : IDiscordBotService
{
    private readonly ILoggerService _loggerService;
    private readonly IConfigurationService _configurationService;
    
    // Implementation with dependency injection
}
```

### Repository Pattern (via EF Core)
```csharp
public class Schedule
{
    public async Task Update(DBEntities? db = null)
    {
        // Entity-based repository pattern
        // Handles both insert and update operations
    }
}
```

### Command Pattern (Discord Commands)
```csharp
[SlashCommand("Event", "Post Event.")]
[SlashRequireUserPermissions(Permissions.ManageMessages)]
public async Task PostEvent(InteractionContext ctx, ...)
{
    // Command implementation
}
```

### Factory Pattern (Service Configuration)
```csharp
private void ConfigureServices(IServiceCollection services)
{
    services.AddSingleton<ILoggerService, LoggerService>();
    services.AddSingleton<IConfigurationService, ConfigurationService>();
    // Service factory pattern
}
```

## Component Relationships

### Core Services Dependency Graph
```
ApplicationHost
├── LoggerService (no dependencies)
├── ConfigurationService (depends on LoggerService)
├── DatabaseService (depends on ConfigurationService, LoggerService)
├── WebApiService (depends on LoggerService, ConfigurationService, DatabaseService)
└── DiscordBotService (depends on LoggerService, ConfigurationService)
```

### Discord Bot Internal Structure
```
DiscordBotService
├── CommandHandler (slash command processing)
├── InteractivityHandler (button/modal interactions)
├── Scheduler (background event processing)
└── DatabaseHandler (database initialization)
```

## Critical Implementation Paths

### Event Creation Flow
1. **Command Validation**: Parameter validation and permission checks
2. **Role Creation**: Discord role generation with unique naming
3. **Database Persistence**: Schedule entity creation and storage
4. **Message Creation**: Rich embed generation and posting
5. **Event ID Assignment**: Message ID stored for future reference

### Event Lifecycle Management
1. **Scheduler Monitoring**: Timer-based checking every minute
2. **Pre-Event Processing**: Thread creation 1 hour before start
3. **Event Completion**: Status updates and message modifications
4. **Cleanup Processing**: Role deletion 1 hour after end

### API Request Processing
1. **Authentication**: API key validation (currently disabled)
2. **Parameter Validation**: Query parameter sanitization
3. **Database Query**: EF Core LINQ query construction
4. **Response Serialization**: JSON response with pagination metadata

### Automation Integration Flow (Planned)
1. **External Trigger**: N8n/automation tool calls API endpoint
2. **Event State Change**: [`Controllers/EventsController.cs`](Controllers/EventsController.cs:1) processes state update
3. **Discord Notification**: [`Services/DiscordBotService.cs`](Services/DiscordBotService.cs:1) pings role programmatically
4. **VRChat Integration**: [`Services/VRChatService.cs`](Services/VRChatService.cs:1) sends invites to linked users
5. **Audit Logging**: State changes logged for tracking and debugging

### Server Event API Flow (Planned)
1. **Server Validation**: Verify API access to specific Discord server
2. **Event Filtering**: Apply date range, status, and type filters
3. **Data Enrichment**: Include Discord metadata and attendance data
4. **Response Formatting**: Structured JSON with pagination and server context

## Error Handling Patterns

### Retry Logic
```csharp
int retryCount = 0;
const int maxRetries = 3;

while (retryCount < maxRetries)
{
    try
    {
        // Operation attempt
        break;
    }
    catch (Exception ex)
    {
        retryCount++;
        await Task.Delay(5000);
    }
}
```

### Graceful Degradation
- Discord bot continues if Web API fails
- Web API operates independently of Discord bot
- Database connection retries with exponential backoff
- Missing configuration falls back to defaults

### Transaction Management
```csharp
await using var transaction = await db.Database.BeginTransactionAsync();
try
{
    // Multiple operations
    await transaction.CommitAsync();
}
catch
{
    await transaction.RollbackAsync();
    throw;
}
```

## Performance Considerations

### Database Optimization
- **Eager Loading**: Include() for related entities when needed
- **Lazy Loading**: Disabled to prevent N+1 queries
- **Connection Pooling**: EF Core built-in connection pooling
- **Query Optimization**: LINQ to SQL translation monitoring

### Memory Management
- **Disposal Patterns**: Using statements for IDisposable resources
- **Service Lifetimes**: Singleton for stateless services
- **Background Tasks**: Proper task cleanup and cancellation

### Caching Strategy
- **No Application Cache**: Direct database queries for consistency
- **Discord Cache**: DSharpPlus built-in caching for Discord entities
- **Static Data**: Environment variables cached at startup