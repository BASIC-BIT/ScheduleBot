using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using DSharpPlus.Entities;

namespace SchedulingAssistant.Entities
{
    public class Ticket
    {
        [Key]
        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
        public int TicketId { get; set; }
        
        [Required]
        public string TicketType { get; set; } = string.Empty;
        
        [Required]
        public ulong CreatorUserId { get; set; }
        
        [Required]
        public string CreatorUsername { get; set; } = string.Empty;
        
        [Required]
        public ulong ServerId { get; set; }
        
        [Description("Message Id of the Thread")]
        public ulong? ThreadId { get; set; }
        
        [Description("Id of the assigned staff member")]
        public ulong? AssignedStaffUserId { get; set; }
        
        [Required]
        public string Status { get; set; } = "open";
        
        [Required]
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        
        public DateTime? ClosedAt { get; set; }
        
        public string? ClosureReason { get; set; }
        
        // Navigation property for ticket messages
        public virtual List<TicketMessage> Messages { get; set; } = new List<TicketMessage>();
        
        // Helper method to build a Discord embed for this ticket
        public DiscordEmbed BuildEmbed(bool includeMessages = false)
        {
            var embed = new DiscordEmbedBuilder()
                .WithTitle($"Ticket #{TicketId}: {TicketType}")
                .WithDescription($"Created by {CreatorUsername}")
                .AddField("Status", Status, true)
                .AddField("Created At", CreatedAt.ToString("yyyy-MM-dd HH:mm:ss"), true)
                .WithColor(Status == "open" ? DiscordColor.Green : DiscordColor.Red);
            
            if (AssignedStaffUserId.HasValue)
            {
                embed.AddField("Assigned To", $"<@{AssignedStaffUserId}>", true);
            }
            
            if (Status == "closed" && ClosedAt.HasValue)
            {
                embed.AddField("Closed At", ClosedAt.Value.ToString("yyyy-MM-dd HH:mm:ss"), true);
                
                if (!string.IsNullOrEmpty(ClosureReason))
                {
                    embed.AddField("Closure Reason", ClosureReason);
                }
            }
            
            if (includeMessages && Messages.Count > 0)
            {
                var messageContent = string.Join("\n", Messages.Take(5).Select(m => $"**{m.SenderUsername}**: {m.MessageContent}"));
                if (Messages.Count > 5)
                {
                    messageContent += $"\n... and {Messages.Count - 5} more messages";
                }
                embed.AddField("Recent Messages", messageContent);
            }
            
            return embed.Build();
        }
    }
} 