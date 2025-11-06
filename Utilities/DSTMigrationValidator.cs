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
        /// Formats a human-readable description of the adjustment magnitude and direction.
        /// </summary>
        /// <param name="hoursAdjustment">Number of hours to adjust. Positive moves forward, negative moves backward.</param>
        /// <returns>Description text such as "forward by 1 hour".</returns>
        public static string FormatAdjustmentDescription(int hoursAdjustment)
        {
            if (hoursAdjustment == 0)
            {
                throw new ArgumentException("Hour adjustment must not be zero.", nameof(hoursAdjustment));
            }

            var magnitude = Math.Abs(hoursAdjustment);
            var direction = hoursAdjustment > 0 ? "forward" : "backward";
            var unit = magnitude == 1 ? "hour" : "hours";

            return $"{direction} by {magnitude} {unit}";
        }

        /// <summary>
        /// Generates a preview of the changes that would be made
        /// </summary>
        /// <param name="dbContext">Database context to use</param>
        /// <param name="hoursAdjustment">Number of hours to adjust (positive moves forward, negative moves backward)</param>
        /// <returns>A string containing the preview report</returns>
        public static async Task<string> GeneratePreviewReportAsync(DBEntities dbContext, int hoursAdjustment)
        {
            if (hoursAdjustment == 0)
            {
                throw new ArgumentException("Hour adjustment must not be zero.", nameof(hoursAdjustment));
            }

            var affectedEvents = await GetAffectedEventsAsync(dbContext);

            if (!affectedEvents.Any())
            {
                return "No future events found that would be affected by the migration.";
            }

            var adjustmentDescription = FormatAdjustmentDescription(hoursAdjustment);

            var output = new StringBuilder();
            output.AppendLine($"📅 **DST Fix Preview** - {affectedEvents.Count} events will be adjusted {adjustmentDescription}\n");
            output.AppendLine($"The following events will be adjusted {adjustmentDescription}:\n");

            var sampleEvents = affectedEvents.Take(5).ToList();
            foreach (var evt in sampleEvents)
            {
                var currentStart = evt.StartTime;
                var currentEnd = evt.EndTime;
                var newStart = currentStart.AddHours(hoursAdjustment);
                var newEnd = currentEnd.AddHours(hoursAdjustment);

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

            output.AppendLine("To apply these changes, run `/FixDSTTimes migrate` with the same adjustment value.");
            return output.ToString();
        }

        /// <summary>
        /// Performs the DST adjustment on future events
        /// </summary>
        /// <param name="dbContext">Database context to use</param>
        /// <param name="hoursAdjustment">Number of hours to adjust (positive moves forward, negative moves backward)</param>
        /// <returns>Number of adjusted events</returns>
        public static async Task<int> PerformDSTAdjustmentAsync(DBEntities dbContext, int hoursAdjustment)
        {
            if (hoursAdjustment == 0)
            {
                throw new ArgumentException("Hour adjustment must not be zero.", nameof(hoursAdjustment));
            }

            var affectedEvents = await GetAffectedEventsAsync(dbContext);

            if (!affectedEvents.Any())
            {
                return 0;
            }

            foreach (var evt in affectedEvents)
            {
                evt.StartTime = evt.StartTime.AddHours(hoursAdjustment);
                evt.EndTime = evt.EndTime.AddHours(hoursAdjustment);
                await evt.Update(dbContext);
            }

            return affectedEvents.Count;
        }
    }
}
