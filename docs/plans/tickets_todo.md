# Ticketing System Implementation Checklist

Below is a comprehensive checklist based on the phased blueprint and iterative steps we discussed. Use this as a “to-do” guide, marking off each item as you complete it.

---

## **Chunk A: Project & Database Setup**

- [ ] **Set Up Branch & Environment**  
  - [ ] Create a new Git branch (e.g., `feature/ticket-system`)  
  - [ ] Confirm your .NET version and DSharpPlus references  
  - [ ] Install/configure MySQL libraries or EF Core MySQL provider  
  - [ ] Add environment variables for Discord token, database credentials

- [ ] **Initialize MySQL Connection**  
  - [ ] Implement logic to connect to the MySQL database at startup  
  - [ ] Log success/failure to console or logs  
  - [ ] Confirm basic error handling and fallback behavior

---

## **Chunk B: Basic Ticket Schema & Models**

- [ ] **Create Ticket Data Models**  
  - [ ] Define `Ticket` with fields:  
    - [ ] `TicketId` (PK, auto-increment)  
    - [ ] `TicketType`, `CreatorUserId`, `CreatorUsername`  
    - [ ] `Status`, `CreatedAt`, `ClosedAt` (nullable), `ClosureReason` (nullable)  
  - [ ] Define `TicketMessage` with fields:  
    - [ ] `MessageId` (PK, auto-increment)  
    - [ ] `TicketId` (FK to `Ticket`)  
    - [ ] `SenderUserId`, `MessageContent`, `Timestamp`

- [ ] **Database Migration or Table Creation**  
  - [ ] Implement EF Core migration or manual SQL script  
  - [ ] Verify tables create successfully in MySQL

- [ ] **Initial Test of DB Operations**  
  - [ ] Insert a test `Ticket` and `TicketMessage`  
  - [ ] Retrieve them to confirm read/write works

---

## **Chunk C: Ticket Commands (Open/Close)**

- [ ] **Implement "/ticket open" Command**  
  - [ ] Prompt user for ticket type (staff application, guru, bot/issue, etc.)  
  - [ ] Insert a new row into the `Ticket` table with `Status = "open"`

- [ ] **Implement "/ticket close" Command**  
  - [ ] Prompt for optional closure reason  
  - [ ] Update the `Ticket` row to `Status="closed"`, set `ClosedAt`, record `ClosureReason`  
  - [ ] Return a confirmation message

- [ ] **Test Open/Close Commands**  
  - [ ] Validate the correct ticket states and DB entries  
  - [ ] Confirm slash commands are registered and accessible

---

## **Chunk D: Private Thread Creation & Templated Questions**

- [ ] **Thread/Channel Creation Logic**  
  - [ ] When `/ticket open` succeeds, create a private thread  
  - [ ] Restrict visibility to ticket creator + staff roles

- [ ] **Templated Questions & Auto-Posting**  
  - [ ] Store question sets (staff application, guru, issue report)  
  - [ ] Post them automatically in the newly created thread

- [ ] **Capturing User Responses**  
  - [ ] Listen for messages in the thread  
  - [ ] Insert each response into `TicketMessage` with correct `SenderUserId`, `MessageContent`, `Timestamp`

- [ ] **Permissions & Validation**  
  - [ ] Ensure ticket creator and staff are the only ones with read/write  
  - [ ] Test error handling if unauthorized user attempts to view or respond

---

## **Chunk E: Ticket Lists & Histories**

- [ ] **"/ticket list" for Open Tickets**  
  - [ ] Display each ticket’s ID, type, creator, creation date, etc.  
  - [ ] Provide a link or mention to its associated thread if desired

- [ ] **Closing & Logging**  
  - [ ] Enhance `/ticket close` to post a summary of final messages or status in a "Ticket Histories" channel  
  - [ ] Remove the closed ticket from the “Tickets List” channel  
  - [ ] Archive/lock the associated thread

- [ ] **Database & Channel Logging**  
  - [ ] Confirm ticket remains in MySQL for historical records  
  - [ ] Check the “Ticket Histories” channel log is properly formatted

---

## **Chunk F: Admin Controls & Assignment**

- [ ] **Assignment Slash Commands**  
  - [ ] `/ticket assign <ticketId> <@staff>` to set `assigned_staff_user_id`  
  - [ ] Update permissions in the private thread to grant staff access

- [ ] **"/ticket add-user" Command**  
  - [ ] Allow admins to add another user to the ticket thread  
  - [ ] Properly handle thread permission overrides

- [ ] **Permission Checks**  
  - [ ] Limit these commands to admin or moderator roles only  
  - [ ] Handle errors if unauthorized user attempts them

---

## **Chunk G: Role-Based Notifications & Weekly Alerts**

- [ ] **Role-Based Notifications**  
  - [ ] Add `/ticket config notifications` to toggle role pings for new tickets  
  - [ ] If enabled, mention the configured role (e.g., @TicketStaff) upon ticket creation

- [ ] **Weekly Reminders for Aging Tickets**  
  - [ ] Implement a scheduled job or background task to find tickets older than 7 days  
  - [ ] Post a reminder in a designated channel weekly until resolved  
  - [ ] Allow a channel or role to be configured for these reminders

---

## **Chunk H: Testing & Validation**

- [ ] **Unit Tests**  
  - [ ] Test ticket creation, closure, message insertion  
  - [ ] Test edge cases (invalid ticket ID, multiple open tickets, etc.)

- [ ] **Integration Tests**  
  - [ ] Simulate `/ticket open` → user replies → `/ticket close` workflow  
  - [ ] Validate correct channel/thread creation, DB entries, final closure logs

- [ ] **Performance & Load Tests (Optional)**  
  - [ ] Confirm the bot handles concurrency for ~20 open tickets smoothly  
  - [ ] Evaluate DB performance with minimal concurrency

---

## **Chunk I: Final Cleanup & Documentation**

- [ ] **Docstrings & Comments**  
  - [ ] Add summary description to commands, classes, and methods  
  - [ ] Clarify usage in line with best practices

- [ ] **README & Setup Guide**  
  - [ ] Document environment configuration (`.env`, appsettings)  
  - [ ] Explain how to run, test, and deploy the bot  
  - [ ] Include a migration or upgrade guide if replacing an older ticket bot

- [ ] **Merge & Review**  
  - [ ] Merge `feature/ticket-system` branch after QA sign-off  
  - [ ] Tag the release and update release notes if applicable

---

## **Done!**

Once you’ve checked off all the above items, you should have a fully functional, documented, and tested ticketing system integrated with your Discord bot. Good luck!
