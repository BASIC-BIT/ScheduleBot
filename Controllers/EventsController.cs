using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using SchedulingAssistant.Entities;
using SchedulingAssistant.Services;
using System;
using System.Linq;
using System.Threading.Tasks;

namespace SchedulingAssistant.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class EventsController : ControllerBase
    {
        private readonly DBEntities _dbContext;
        private readonly ILogger<EventsController> _logger;

        public EventsController(DBEntities dbContext, ILogger<EventsController> logger)
        {
            _dbContext = dbContext;
            _logger = logger;
        }

        // GET: api/events
        [HttpGet]
        public async Task<IActionResult> GetEvents(
            [FromQuery] int page = 1,
            [FromQuery] int pageSize = 10,
            [FromQuery] ulong? serverId = null,
            [FromQuery] DateTime? startDate = null,
            [FromQuery] DateTime? endDate = null,
            [FromQuery] bool? isActive = null,
            [FromQuery] bool? hasEnded = null)
        {
            // Validate and cap page size
            if (pageSize <= 0) pageSize = 10;
            if (pageSize > 50) pageSize = 50;
            if (page <= 0) page = 1;

            try
            {
                // Start with all schedules
                IQueryable<Schedule> query = _dbContext.Schedules;

                // Apply filters
                if (serverId.HasValue)
                    query = query.Where(s => s.ServerId == serverId.Value);

                if (startDate.HasValue)
                    query = query.Where(s => s.StartTime >= startDate.Value);

                if (endDate.HasValue)
                    query = query.Where(s => s.EndTime <= endDate.Value);

                if (isActive.HasValue)
                    query = query.Where(s => s.IsActive == isActive.Value);

                // Default behavior: Only show events that haven't ended yet
                // unless hasEnded filter is explicitly provided
                if (hasEnded.HasValue)
                    query = query.Where(s => s.HasEnded == hasEnded.Value);
                else
                    query = query.Where(s => !s.HasEnded);

                // Get total count for pagination
                var totalItems = await query.CountAsync();
                var totalPages = (int)Math.Ceiling(totalItems / (double)pageSize);

                // Apply pagination with chronological ordering by start time
                var events = await query
                    .OrderBy(s => s.StartTime)
                    .Skip((page - 1) * pageSize)
                    .Take(pageSize)
                    .Select(s => new
                    {
                        id = s.Id,
                        eventTitle = s.EventTitle,
                        eventDescription = s.EventDescription,
                        startTime = s.StartTime,
                        endTime = s.EndTime,
                        hostName = s.HostName,
                        worldLink = s.WorldLink,
                        imageUrl = s.ImageURL,
                        isActive = s.IsActive,
                        hasEnded = s.HasEnded
                    })
                    .ToListAsync();

                // Construct response
                var response = new
                {
                    pagination = new
                    {
                        currentPage = page,
                        pageSize = pageSize,
                        totalItems = totalItems,
                        totalPages = totalPages
                    },
                    events = events
                };

                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error retrieving events");
                return StatusCode(500, new { error = "An error occurred while retrieving events." });
            }
        }
    }
} 