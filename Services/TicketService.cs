using DSharpPlus;
using DSharpPlus.Entities;
using DSharpPlus.EventArgs;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using SchedulingAssistant.Entities;
using System;
using System.Threading.Tasks;

namespace SchedulingAssistant.Services
{
    public class TicketService
    {
        private readonly IServiceProvider _services;
        private readonly ILogger<TicketService> _logger;
        private readonly DiscordClient _client;
        
        public TicketService(IServiceProvider services)
        {
            _services = services;
            _logger = _services.GetRequiredService<ILogger<TicketService>>();
            _client = _services.GetRequiredService<DiscordClient>();
        }
        
        public Task Initialize()
        {
            _logger.LogInformation("Initializing Ticket Service");
            
            // Register message created event handler
            _client.MessageCreated += OnMessageCreated;
            
            _logger.LogInformation("Ticket Service Initialized");
            return Task.CompletedTask;
        }
        
        private async Task OnMessageCreated(DiscordClient sender, MessageCreateEventArgs e)
        {
            // Ignore messages from bots
            if (e.Author.IsBot)
                return;
            
            try
            {
                // Check if this message is in a ticket thread
                using var db = new DBEntities();
                var ticket = await db.Tickets
                    .FirstOrDefaultAsync(t => t.ThreadId == e.Channel.Id && t.Status == "open");
                
                if (ticket == null)
                    return;
                
                // This is a message in a ticket thread, so log it
                var ticketMessage = new TicketMessage
                {
                    TicketId = ticket.TicketId,
                    SenderUserId = e.Author.Id,
                    SenderUsername = e.Author.Username,
                    MessageContent = e.Message.Content,
                    Timestamp = DateTime.UtcNow
                };
                
                db.TicketMessages.Add(ticketMessage);
                await db.SaveChangesAsync();
                
                _logger.LogDebug($"Logged message in ticket #{ticket.TicketId} from {e.Author.Username}");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error logging ticket message");
            }
        }
        
        public async Task<DiscordChannel> GetTicketHistoriesChannel(DiscordGuild guild)
        {
            // Try to find a channel named "ticket-histories"
            var channels = await guild.GetChannelsAsync();
            var ticketHistoriesChannel = channels.FirstOrDefault(c => c.Name.ToLower() == "ticket-histories");
            
            if (ticketHistoriesChannel == null)
            {
                // Create the channel if it doesn't exist
                _logger.LogInformation($"Creating ticket-histories channel in guild {guild.Name}");
                
                ticketHistoriesChannel = await guild.CreateChannelAsync(
                    "ticket-histories",
                    ChannelType.Text,
                    null,
                    "Channel for ticket history logs");
                
                // Set permissions to restrict viewing to staff
                var everyoneRole = guild.EveryoneRole;
                await ticketHistoriesChannel.AddOverwriteAsync(everyoneRole, Permissions.None, Permissions.AccessChannels);
                
                // TODO: Add overwrites for staff roles
            }
            
            return ticketHistoriesChannel;
        }
        
        public async Task<DiscordChannel> GetTicketsListChannel(DiscordGuild guild)
        {
            // Try to find a channel named "tickets-list"
            var channels = await guild.GetChannelsAsync();
            var ticketsListChannel = channels.FirstOrDefault(c => c.Name.ToLower() == "tickets-list");
            
            if (ticketsListChannel == null)
            {
                // Create the channel if it doesn't exist
                _logger.LogInformation($"Creating tickets-list channel in guild {guild.Name}");
                
                ticketsListChannel = await guild.CreateChannelAsync(
                    "tickets-list",
                    ChannelType.Text,
                    null,
                    "Channel for active tickets list");
                
                // Set permissions to restrict viewing to staff
                var everyoneRole = guild.EveryoneRole;
                await ticketsListChannel.AddOverwriteAsync(everyoneRole, Permissions.None, Permissions.AccessChannels);
                
                // TODO: Add overwrites for staff roles
            }
            
            return ticketsListChannel;
        }
        
        public async Task UpdateTicketsListChannel(DiscordGuild guild)
        {
            try
            {
                var ticketsListChannel = await GetTicketsListChannel(guild);
                
                // Get all open tickets for this server
                using var db = new DBEntities();
                var tickets = await db.Tickets
                    .Where(t => t.ServerId == guild.Id && t.Status == "open")
                    .OrderByDescending(t => t.CreatedAt)
                    .ToListAsync();
                
                // Clear the channel
                var messages = await ticketsListChannel.GetMessagesAsync(100);
                await ticketsListChannel.DeleteMessagesAsync(messages);
                
                if (tickets.Count == 0)
                {
                    await ticketsListChannel.SendMessageAsync("There are no open tickets.");
                    return;
                }
                
                // Post a message for each ticket
                foreach (var ticket in tickets)
                {
                    await ticketsListChannel.SendMessageAsync(new DiscordMessageBuilder()
                        .AddEmbed(ticket.BuildEmbed()));
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error updating tickets list channel");
            }
        }
        
        public async Task LogTicketClosure(Ticket ticket, DiscordGuild guild, string closedBy)
        {
            try
            {
                var ticketHistoriesChannel = await GetTicketHistoriesChannel(guild);
                
                // Get the ticket messages
                using var db = new DBEntities();
                var messages = await db.TicketMessages
                    .Where(m => m.TicketId == ticket.TicketId)
                    .OrderBy(m => m.Timestamp)
                    .ToListAsync();
                
                // Create an embed for the ticket
                var embed = new DiscordEmbedBuilder()
                    .WithTitle($"Ticket #{ticket.TicketId}: {ticket.TicketType}")
                    .WithDescription($"Created by {ticket.CreatorUsername}")
                    .AddField("Status", "Closed", true)
                    .AddField("Created At", ticket.CreatedAt.ToString("yyyy-MM-dd HH:mm:ss"), true)
                    .AddField("Closed At", ticket.ClosedAt?.ToString("yyyy-MM-dd HH:mm:ss") ?? "Unknown", true)
                    .AddField("Closed By", closedBy, true)
                    .WithColor(DiscordColor.Red);
                
                if (!string.IsNullOrEmpty(ticket.ClosureReason))
                {
                    embed.AddField("Closure Reason", ticket.ClosureReason);
                }
                
                // Add the messages to the embed
                if (messages.Count > 0)
                {
                    var messageContent = string.Join("\n", messages.Take(10).Select(m => $"**{m.SenderUsername}**: {m.MessageContent}"));
                    if (messages.Count > 10)
                    {
                        messageContent += $"\n... and {messages.Count - 10} more messages";
                    }
                    embed.AddField("Messages", messageContent);
                }
                
                // Post the embed
                await ticketHistoriesChannel.SendMessageAsync(new DiscordMessageBuilder()
                    .AddEmbed(embed));
                
                // Update the tickets list channel
                await UpdateTicketsListChannel(guild);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error logging ticket closure");
            }
        }
    }
} 