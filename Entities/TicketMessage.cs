using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace SchedulingAssistant.Entities
{
    public class TicketMessage
    {
        [Key]
        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
        public int MessageId { get; set; }
        
        [Required]
        public int TicketId { get; set; }
        
        [Required]
        public ulong SenderUserId { get; set; }
        
        [Required]
        public string SenderUsername { get; set; } = string.Empty;
        
        [Required]
        public string MessageContent { get; set; } = string.Empty;
        
        [Required]
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
        
        // Navigation property back to the ticket
        [ForeignKey("TicketId")]
        public virtual Ticket Ticket { get; set; }
    }
} 