# Discord Bot Ticketing System

This is a comprehensive ticketing system for Discord bots, built with C# and DSharpPlus. It allows users to create, manage, and track tickets within Discord servers.

## Features

- **Ticket Creation**: Users can open tickets of different types (Staff Applications, Guru Applications, Issue Reports)
- **Ticket Management**: Staff can view, assign, and close tickets
- **Thread-Based Conversations**: Each ticket creates a private thread for discussion
- **Message Tracking**: All messages in ticket threads are logged to the database
- **Ticket History**: Closed tickets are archived and summarized in a dedicated channel
- **Ticket List**: Active tickets are displayed in a dedicated channel for staff reference

## Commands

The ticketing system provides the following slash commands:

- `/ticket open [type]` - Opens a new ticket of the specified type
- `/ticket close [reason]` - Closes the current ticket with an optional reason
- `/ticket list` - Lists all open tickets (staff only)
- `/ticket refresh` - Refreshes the tickets list channel (staff only)

## Database Structure

The ticketing system uses two main database tables:

### Tickets Table

| Column | Type | Description |
|--------|------|-------------|
| TicketId | int | Primary key, auto-incremented |
| TicketType | string | Type of ticket (StaffApplication, GuruApplication, IssueReport) |
| CreatorUserId | ulong | Discord ID of the user who created the ticket |
| CreatorUsername | string | Username of the user who created the ticket |
| ServerId | ulong | Discord ID of the server where the ticket was created |
| ThreadId | ulong | Discord ID of the thread associated with the ticket |
| AssignedStaffUserId | ulong | Discord ID of the staff member assigned to the ticket (optional) |
| Status | string | Current status of the ticket (open, closed) |
| CreatedAt | DateTime | When the ticket was created |
| ClosedAt | DateTime | When the ticket was closed (optional) |
| ClosureReason | string | Reason for closing the ticket (optional) |

### TicketMessages Table

| Column | Type | Description |
|--------|------|-------------|
| MessageId | int | Primary key, auto-incremented |
| TicketId | int | Foreign key to the Tickets table |
| SenderUserId | ulong | Discord ID of the message sender |
| SenderUsername | string | Username of the message sender |
| MessageContent | string | Content of the message |
| Timestamp | DateTime | When the message was sent |

## Channels

The ticketing system creates and manages two special channels:

- **ticket-histories**: Contains summaries of closed tickets
- **tickets-list**: Contains a list of all open tickets

## Setup

1. The ticketing system is automatically initialized when the bot starts
2. The necessary database tables are created if they don't exist
3. The special channels are created if they don't exist
4. Permissions are set to restrict access to staff members

## Permissions

- Regular users can open tickets and close their own tickets
- Staff members (users with the "Manage Channels" permission) can:
  - View all tickets
  - Close any ticket
  - View the ticket histories and tickets list channels

## Future Enhancements

- Ticket assignment system for staff members
- Ticket categories and priorities
- Ticket templates for different types
- Ticket statistics and reporting
- Ticket search functionality
