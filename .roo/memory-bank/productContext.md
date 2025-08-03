# ScheduleBot Product Context

## Why This Project Exists

### Problem Statement
Discord communities, particularly VRChat and gaming communities, struggle with:
- **Manual Event Management**: Creating and tracking events across multiple platforms
- **Attendance Coordination**: Difficulty knowing who will attend events
- **Role Management**: Manual assignment and cleanup of event-specific roles
- **Cross-Platform Integration**: No easy way to share event data with external applications
- **Event Discovery**: Events get lost in chat history without persistent visibility

### Target Users
- **Primary**: Discord server administrators and moderators
- **Secondary**: Event organizers and community managers
- **Tertiary**: VRChat world creators needing event data integration

## How It Should Work

### User Experience Goals
1. **Simplicity**: One-command event creation with rich, interactive displays
2. **Automation**: Minimal manual intervention for routine tasks
3. **Visibility**: Events remain prominently displayed until completion
4. **Integration**: Seamless data sharing with external platforms
5. **Reliability**: Consistent operation without manual maintenance

### Core User Flows

#### Event Creation Flow
1. Admin uses `/Event` slash command with event details
2. Bot creates Discord role automatically
3. Rich embed posted in designated events channel
4. Users interact with reactions to indicate attendance
5. Bot manages role assignments based on attendance

#### Event Lifecycle Flow
1. **Pre-Event**: Thread created 1 hour before start time
2. **During Event**: Attendance tracked and role maintained
3. **Post-Event**: Event marked as ended, role cleanup scheduled
4. **Cleanup**: Role deleted 1 hour after event completion

#### External Integration Flow
1. External application queries REST API endpoints
2. Event data returned in standardized JSON format
3. Images served from S3 bucket with public access
4. Pagination and filtering support for large datasets

## Problems It Solves

### For Discord Communities
- **Event Visibility**: Persistent, interactive event displays
- **Attendance Management**: Clear tracking of who's attending
- **Role Automation**: Automatic creation, assignment, and cleanup
- **Thread Organization**: Dedicated discussion spaces for events
- **Administrative Control**: Easy editing, deletion, and management

### For VRChat Integration
- **Data Access**: REST API provides event information to UDON scripts
- **Image Hosting**: S3-hosted images accessible in VRChat worlds
- **Real-time Updates**: Current event status and attendance data
- **Low Bandwidth**: Optimized JSON responses for VRChat consumption

### For Event Organizers
- **Bulk Operations**: CSV import/export for large event sets
- **Time Management**: Automatic timezone handling and DST adjustments
- **Reporting**: Attendance reports and analytics
- **Flexibility**: Rich editing capabilities and event templates

## Success Metrics
- **Adoption**: Number of Discord servers using the bot
- **Engagement**: Event attendance rates and user interactions
- **Reliability**: Uptime and successful event processing
- **Integration**: External API usage and VRChat world implementations
- **Community**: GitHub stars, contributions, and community feedback

## Future Vision
- **Enhanced Analytics**: Detailed event and attendance analytics
- **Multi-Platform**: Support for additional platforms beyond Discord
- **Advanced Scheduling**: Recurring events and complex scheduling
- **Customization**: Configurable templates and branding options
- **Mobile Support**: Companion mobile app for event management