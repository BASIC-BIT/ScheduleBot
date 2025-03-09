using Microsoft.EntityFrameworkCore;
using SchedulingAssistant.Entities;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SchedulingAssistant.Utilities
{
    /// <summary>
    /// Utility class to help validate and perform the DST time adjustment migration
    /// </summary>
    public class DSTMigrationValidator
    {
        /// <summary>
        /// Gets a list of future events that would be affected by the DST adjustment
        /// </summary>
        /// <param name="dbContext">Database context to use</param>
        /// <returns>List of affected Schedule entities</returns>
        public static async Task<List<Schedule>> GetAffectedEventsAsync(DBEntities dbContext)
        {
            var now = DateTime.UtcNow.Date;

            return await dbContext.Schedules
                .Where(s => s.StartTime >= now)
                .OrderBy(s => s.StartTime)
                .ToListAsync();
        }

        /// <summary>
        /// Generates a preview of the changes that would be made
        /// </summary>
        /// <param name="dbContext">Database context to use</param>
        /// <returns>A string containing the preview report</returns>
        public static async Task<string> GeneratePreviewReportAsync(DBEntities dbContext)
        {
            var affectedEvents = await GetAffectedEventsAsync(dbContext);
            
            if (!affectedEvents.Any())
            {
                return "No future events found that would be affected by the migration.";
            }

            var output = new StringBuilder();
            output.AppendLine($"📅 **DST Fix Preview** - {affectedEvents.Count} events will be adjusted\n");
            output.AppendLine("The following events will be adjusted backward by 1 hour:\n");
            
            // Show detailed info for up to 5 events as examples
            var sampleEvents = affectedEvents.Take(5).ToList();
            foreach (var evt in sampleEvents)
            {
                var currentStart = evt.StartTime;
                var currentEnd = evt.EndTime;
                var newStart = currentStart.AddHours(-1);
                var newEnd = currentEnd.AddHours(-1);
                
                output.AppendLine($"**{evt.EventTitle}**");
                output.AppendLine($"- Current start: {currentStart:yyyy-MM-dd HH:mm} UTC");
                output.AppendLine($"- New start: {newStart:yyyy-MM-dd HH:mm} UTC");
                output.AppendLine($"- Current end: {currentEnd:yyyy-MM-dd HH:mm} UTC");
                output.AppendLine($"- New end: {newEnd:yyyy-MM-dd HH:mm} UTC\n");
            }
            
            if (affectedEvents.Count > 5)
            {
                output.AppendLine($"...and {affectedEvents.Count - 5} more events\n");
            }
            
            return output.ToString();
        }

        /// <summary>
        /// Performs the DST adjustment on future events
        /// </summary>
        /// <param name="dbContext">Database context to use</param>
        /// <returns>Number of adjusted events</returns>
        public static async Task<int> PerformDSTAdjustmentAsync(DBEntities dbContext)
        {
            var affectedEvents = await GetAffectedEventsAsync(dbContext);
            
            if (!affectedEvents.Any())
            {
                return 0;
            }

            foreach (var evt in affectedEvents)
            {
                evt.StartTime = evt.StartTime.AddHours(-1);
                evt.EndTime = evt.EndTime.AddHours(-1);
                await evt.Update(dbContext);
            }

            return affectedEvents.Count;
        }
    }
}