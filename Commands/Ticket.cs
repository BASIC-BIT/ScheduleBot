using DSharpPlus;
using DSharpPlus.Entities;
using DSharpPlus.SlashCommands;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using SchedulingAssistant.Entities;
using SchedulingAssistant.Services;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace SchedulingAssistant.Commands
{
    [SlashCommandGroup("ticket", "Commands for managing tickets")]
    public class TicketCommands : ApplicationCommandModule
    {
        private readonly ILogger<TicketCommands> _logger;
        private readonly IServiceProvider _services;
        private TicketService _ticketService;
        
        public TicketCommands(IServiceProvider services)
        {
            _services = services;
            _logger = _services.GetRequiredService<ILogger<TicketCommands>>();
            _ticketService = _services.GetRequiredService<TicketService>();
        }
        
        [SlashCommand("open", "Open a new ticket")]
        public async Task OpenTicket(InteractionContext ctx,
            [Option("type", "The type of ticket to open")] TicketType ticketType)
        {
            // Defer the response to give us time to process
            await ctx.DeferResponseAsync(true);
            
            try
            {
                // Create a new ticket in the database
                using var db = new DBEntities();
                
                var ticket = new Ticket
                {
                    TicketType = ticketType.ToString(),
                    CreatorUserId = ctx.User.Id,
                    CreatorUsername = ctx.User.Username,
                    ServerId = ctx.Guild.Id,
                    Status = "open",
                    CreatedAt = DateTime.UtcNow
                };
                
                db.Tickets.Add(ticket);
                await db.SaveChangesAsync();
                
                // Create a private thread for this ticket
                var channel = await ctx.Guild.GetChannelAsync(ctx.Channel.Id);
                var thread = await channel.CreateThreadAsync(
                    $"Ticket-{ticket.TicketId}-{ticketType}",
                    ChannelType.PrivateThread,
                    $"Ticket opened by {ctx.User.Username}");
                
                // Update the ticket with the thread ID
                ticket.ThreadId = thread.Id;
                await db.SaveChangesAsync();
                
                // Add the user to the thread
                await thread.AddThreadMemberAsync(ctx.User.Id);
                
                // Post the template questions based on ticket type
                await PostTemplateQuestions(thread, ticketType);
                
                // Update the tickets list channel
                await _ticketService.UpdateTicketsListChannel(ctx.Guild);
                
                // Respond to the user
                await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                    .WithContent($"Ticket #{ticket.TicketId} has been opened. Please check the thread {thread.Mention} to provide more information."));
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error opening ticket");
                await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                    .WithContent("There was an error opening your ticket. Please try again later."));
            }
        }
        
        [SlashCommand("close", "Close an existing ticket")]
        public async Task CloseTicket(InteractionContext ctx,
            [Option("reason", "The reason for closing the ticket")] string reason = null)
        {
            // Defer the response to give us time to process
            await ctx.DeferResponseAsync(true);
            
            try
            {
                // Check if this is a ticket thread
                using var db = new DBEntities();
                var ticket = await db.Tickets
                    .FirstOrDefaultAsync(t => t.ThreadId == ctx.Channel.Id && t.Status == "open");
                
                if (ticket == null)
                {
                    await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                        .WithContent("This command can only be used in an open ticket thread."));
                    return;
                }
                
                // Check if the user is the ticket creator or has the appropriate permissions
                bool isCreator = ticket.CreatorUserId == ctx.User.Id;
                bool isStaff = ctx.Member.Permissions.HasPermission(Permissions.ManageChannels);
                
                if (!isCreator && !isStaff)
                {
                    await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                        .WithContent("You don't have permission to close this ticket."));
                    return;
                }
                
                // Update the ticket status
                ticket.Status = "closed";
                ticket.ClosedAt = DateTime.UtcNow;
                ticket.ClosureReason = reason;
                
                await db.SaveChangesAsync();
                
                // Get the thread
                var thread = await ctx.Guild.GetChannelAsync(ticket.ThreadId.Value);
                
                // Post a message in the thread
                await thread.SendMessageAsync(new DiscordMessageBuilder()
                    .WithContent($"This ticket has been closed by {ctx.User.Mention}" + 
                                (string.IsNullOrEmpty(reason) ? "." : $" with reason: {reason}")));
                
                // Archive the thread
                await thread.ModifyAsync(props => {
                    props.Archived = true;
                    props.Locked = true;
                });
                
                // Log the ticket closure
                await _ticketService.LogTicketClosure(ticket, ctx.Guild, ctx.User.Username);
                
                // Respond to the user
                await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                    .WithContent($"Ticket #{ticket.TicketId} has been closed."));
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error closing ticket");
                await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                    .WithContent("There was an error closing the ticket. Please try again later."));
            }
        }
        
        [SlashCommand("list", "List all open tickets")]
        public async Task ListTickets(InteractionContext ctx)
        {
            // Defer the response to give us time to process
            await ctx.DeferResponseAsync(true);
            
            try
            {
                // Check if the user has the appropriate permissions
                if (!ctx.Member.Permissions.HasPermission(Permissions.ManageChannels))
                {
                    await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                        .WithContent("You don't have permission to list tickets."));
                    return;
                }
                
                // Get all open tickets for this server
                using var db = new DBEntities();
                var tickets = await db.Tickets
                    .Where(t => t.ServerId == ctx.Guild.Id && t.Status == "open")
                    .OrderByDescending(t => t.CreatedAt)
                    .ToListAsync();
                
                if (tickets.Count == 0)
                {
                    await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                        .WithContent("There are no open tickets."));
                    return;
                }
                
                // Create an embed for each ticket
                var embeds = new List<DiscordEmbed>();
                
                foreach (var ticket in tickets)
                {
                    embeds.Add(ticket.BuildEmbed());
                }
                
                // Respond to the user
                await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                    .WithContent($"There are {tickets.Count} open tickets:")
                    .AddEmbeds(embeds));
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error listing tickets");
                await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                    .WithContent("There was an error listing tickets. Please try again later."));
            }
        }
        
        [SlashCommand("refresh", "Refresh the tickets list channel")]
        [SlashCommandPermissions(Permissions.ManageChannels)]
        public async Task RefreshTicketsChannel(InteractionContext ctx)
        {
            await ctx.DeferResponseAsync(true);
            
            try
            {
                await _ticketService.UpdateTicketsListChannel(ctx.Guild);
                
                await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                    .WithContent("Tickets list channel has been refreshed."));
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error refreshing tickets channel");
                await ctx.EditResponseAsync(new DiscordWebhookBuilder()
                    .WithContent("There was an error refreshing the tickets channel. Please try again later."));
            }
        }
        
        private async Task PostTemplateQuestions(DiscordChannel thread, TicketType ticketType)
        {
            string questions = GetTemplateQuestions(ticketType);
            
            await thread.SendMessageAsync(new DiscordMessageBuilder()
                .WithContent(questions));
        }
        
        private string GetTemplateQuestions(TicketType ticketType)
        {
            switch (ticketType)
            {
                case TicketType.StaffApplication:
                    return "Welcome!!\n" +
                        "The Faceless are currently looking for members to fill these roles:\n" +
                        "Community Manager\n" +
                        "Host\n" +
                        "Moderator\n" +
                        "Discord Admin\n" +
                        "Promoter\n" +
                        "New Community Outreach\n\n" +
                        "Please let us know any and all positions that interest you!\n" +
                        "Question 1:\n" +
                        "Have you read and agreed to the rules of The Faceless? Are there any rules you don't see that you think should be there or any that you don't think should be there?\n" +
                        "Question 2:\n" +
                        "Please provide your VRC and Discord usernames\n" +
                        "Question 3:\n" +
                        "Have you ever staffed in VRC or for any event venues or clubs (IRL or VR) before? If so, where?\n" +
                        "Question 4:\n" +
                        "Which position(s) are you interested in?\n" +
                        "Question 5:\n" +
                        "When do you have free time normally?\n" +
                        "Question 6:\n" +
                        "What IRL and/or VR responsibilities do you currently have?\n" +
                        "Question 7:\n" +
                        "Do you feel comfortable with possible confrontation or having to mediate issues?\n" +
                        "Question 8:\n" +
                        "If you noticed an argument happening between 2 patrons during an event what steps would you take?\n" +
                        "Question 9:\n" +
                        "If you saw someone discussing politics or religion, what would be your response, if any?\n" +
                        "Question 10:\n" +
                        "How long have you been involved in the VR space if at all?\n" +
                        "Question 11:\n" +
                        "We currently have our staff meetings at 6PM CST on Mondays - are you generally available at that time? (this is NOT a requirement!)\n" +
                        "Question 12:\n" +
                        "Which time zone are you based in?\n" +
                        "Question 13:\n" +
                        "What does being a member of The Faceless mean to you?\n" +
                        "Question 14:\n" +
                        "What do you know about the VRUnderground Oasis, if anything?\n" +
                        "Question 15:\n" +
                        "What do you get on VRChat with?\n" +
                        "Question 16:\n" +
                        "Is there anything that we can do to help make your duties more accessible?\n" +
                        "Question 17:\n" +
                        "Any additional interests and hobbies?\n" +
                        "Question 18:\n" +
                        "Are there any references you might like to provide?";
                
                case TicketType.GuruApplication:
                    return "Thank you for your interest in sharing your knowledge and interest with our group!\n\n" +
                        "Question 1:\n" +
                        "Please let us know the nature of the class you are interested in providing or would like to see added.\n" +
                        "Question 2:\n" +
                        "If you would be the one teaching or giving said class (in any subject/field! some examples include: Tarot, meditation, workouts, dance, philosophy, language, etc...) If not, are you aware of somebody who'd be interested in giving said class?\n" +
                        "Question 3:\n" +
                        "Do you have any credentials or how long have you been practicing?\n" +
                        "Question 4:\n" +
                        "What day of the week and time works best for you to teach your class? Are you interested in running it on a regular cadence (weekly, biweekly, once a month, etc.) or more ad-hoc?\n" +
                        "Question 5:\n" +
                        "What style(s) of class do you want to teach? (ie. lectures, workshops, a club, VR dance, etc.)";
                
                case TicketType.IssueReport:
                    return "What's the issue you're experiencing? If it's a bot or troublesome user, please provide the full discord account name (and User ID if you know how to, no worries if not!), as well as screenshot proof of the issue.\n\n" +
                        "A staff member will get in contact with you as soon as possible! Thank you for your patience.";
                
                default:
                    return "Please provide details about your ticket.";
            }
        }
    }
    
    public enum TicketType
    {
        [ChoiceName("Staff Application")]
        StaffApplication,
        
        [ChoiceName("Guru/Teacher Application")]
        GuruApplication,
        
        [ChoiceName("Issue Report")]
        IssueReport
    }
} 