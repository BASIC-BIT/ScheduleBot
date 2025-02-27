<think>
Let me analyze the code provided in the potential codebase context and the requirements discussed:

1. The application is a scheduling assistant that manages events stored in a MySQL database. It uses Entity Framework Core with a `DBEntities` context.

2. The `Schedule` entity already has an `ImageURL` property that can be null, which means we don't need to add a new field for the image URL.

3. We need to create a new GET endpoint that will expose the schedule data and image URLs for consumption by UDON in VRChat.

4. From the requirements, we need to consider:
   - JSON response format
   - Pagination and filtering with sensible defaults
   - Design for future API key authentication
   - Image hosting in AWS S3 using Terraform

So I need to create a comprehensive specification that addresses all these points with specific implementation details.
</think>

# Developer Specification: VRChat UDON Integration API

## Overview
This specification outlines the implementation of a new GET endpoint that will expose the schedule database information to UDON in VRChat. The endpoint will provide schedule data in a JSON format, including event titles, descriptions, and image URLs. The images will be hosted in an AWS S3 bucket.

## Requirements

### Functional Requirements
1. Create a GET endpoint (`/api/events`) to retrieve schedule data
2. Support pagination with sensible defaults (10 items per page)
3. Support filtering by date range, server ID, and active status
4. Include image URLs in the response, pointing to S3-hosted images
5. Return data in a standardized JSON format compatible with UDON
6. Design for low-bandwidth consumption and quick loading in VRChat

### Technical Requirements
1. Implement the endpoint using ASP.NET Core Web API
2. Set up an S3 bucket using Terraform for image hosting
3. Design with extensibility in mind for future authentication
4. Ensure proper error handling and logging
5. Implement CORS to allow requests from VRChat

## Architecture

### API Endpoint Structure

```
GET /api/events
    - Query Parameters:
        - page (default: 1)
        - pageSize (default: 10, max: 50)
        - serverId (optional)
        - startDate (optional, ISO 8601 format)
        - endDate (optional, ISO 8601 format)
        - isActive (optional, boolean)
        - hasEnded (optional, boolean)
```

### Response Format

```json
{
  "pagination": {
    "currentPage": 1,
    "pageSize": 10,
    "totalItems": 45,
    "totalPages": 5
  },
  "events": [
    {
      "id": 123,
      "eventTitle": "VRChat Meetup",
      "eventDescription": "Let's meet in VRChat!",
      "startTime": "2023-07-15T18:00:00Z",
      "endTime": "2023-07-15T20:00:00Z",
      "hostName": "EventHost",
      "worldLink": "https://vrchat.com/home/world/wrld_abc123",
      "imageUrl": "https://your-s3-bucket.s3.amazonaws.com/events/123.jpg",
      "isActive": true,
      "hasEnded": false
    },
    // More events...
  ]
}
```

### S3 Bucket Architecture
- Bucket name: `scheduling-assistant-event-images`
- Region: Configured via environment variable
- Directory structure: `/events/{event_id}.{extension}`
- Public read access, private write access
- CORS enabled for VRChat domains

## Implementation Plan

### 1. Create API Controller

```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using SchedulingAssistant.Entities;
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

                if (hasEnded.HasValue)
                    query = query.Where(s => s.HasEnded == hasEnded.Value);

                // Get total count for pagination
                var totalItems = await query.CountAsync();
                var totalPages = (int)Math.Ceiling(totalItems / (double)pageSize);

                // Apply pagination
                var events = await query
                    .OrderBy(s => s.StartTime)
                    .Skip((page - 1) * pageSize)
                    .Take(pageSize)
                    .Select(s => new
                    {
                        s.Id,
                        s.EventTitle,
                        s.EventDescription,
                        s.StartTime,
                        s.EndTime,
                        s.HostName,
                        s.WorldLink,
                        s.ImageURL,
                        s.IsActive,
                        s.HasEnded
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
```

### 2. Create Terraform Configuration for S3 Bucket

```terraform
# main.tf
provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "event_images" {
  bucket = var.bucket_name
  
  tags = {
    Name        = "Event Images"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_website_configuration" "event_images_website" {
  bucket = aws_s3_bucket.event_images.id
  
  index_document {
    suffix = "index.html"
  }
}

resource "aws_s3_bucket_public_access_block" "event_images_access" {
  bucket = aws_s3_bucket.event_images.id
  
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "allow_public_read" {
  bucket = aws_s3_bucket.event_images.id
  policy = data.aws_iam_policy_document.allow_public_read.json
}

data "aws_iam_policy_document" "allow_public_read" {
  statement {
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    
    actions = [
      "s3:GetObject"
    ]
    
    resources = [
      "${aws_s3_bucket.event_images.arn}/*"
    ]
  }
}

resource "aws_s3_bucket_cors_configuration" "event_images_cors" {
  bucket = aws_s3_bucket.event_images.id
  
  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# variables.tf
variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "Name of the S3 bucket for event images"
  type        = string
  default     = "scheduling-assistant-event-images"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

# outputs.tf
output "bucket_domain_name" {
  value = aws_s3_bucket.event_images.bucket_regional_domain_name
}

output "bucket_website_endpoint" {
  value = aws_s3_bucket_website_configuration.event_images_website.website_endpoint
}
```

### 3. Add AWS S3 Image Service

```csharp
using Amazon;
using Amazon.S3;
using Amazon.S3.Model;
using Microsoft.Extensions.Configuration;
using System;
using System.IO;
using System.Threading.Tasks;

namespace SchedulingAssistant.Services
{
    public interface IS3ImageService
    {
        Task<string> UploadImageAsync(int eventId, Stream imageStream, string contentType, string fileExtension);
        Task<bool> DeleteImageAsync(int eventId, string fileExtension);
        string GetImageUrl(int eventId, string fileExtension);
    }

    public class S3ImageService : IS3ImageService
    {
        private readonly IAmazonS3 _s3Client;
        private readonly string _bucketName;
        private readonly string _baseUrl;

        public S3ImageService(IConfiguration configuration)
        {
            var accessKey = configuration["AWS:AccessKey"];
            var secretKey = configuration["AWS:SecretKey"];
            var region = configuration["AWS:Region"];
            _bucketName = configuration["AWS:BucketName"];
            
            // Construct the base URL for the S3 bucket
            _baseUrl = configuration["AWS:BaseUrl"] ?? $"https://{_bucketName}.s3.{region}.amazonaws.com";
            
            _s3Client = new AmazonS3Client(accessKey, secretKey, RegionEndpoint.GetBySystemName(region));
        }

        public async Task<string> UploadImageAsync(int eventId, Stream imageStream, string contentType, string fileExtension)
        {
            var key = $"events/{eventId}.{fileExtension}";
            
            var putRequest = new PutObjectRequest
            {
                BucketName = _bucketName,
                Key = key,
                InputStream = imageStream,
                ContentType = contentType,
                CannedACL = S3CannedACL.PublicRead
            };

            await _s3Client.PutObjectAsync(putRequest);
            
            return GetImageUrl(eventId, fileExtension);
        }

        public async Task<bool> DeleteImageAsync(int eventId, string fileExtension)
        {
            var key = $"events/{eventId}.{fileExtension}";
            
            var deleteRequest = new DeleteObjectRequest
            {
                BucketName = _bucketName,
                Key = key
            };

            var response = await _s3Client.DeleteObjectAsync(deleteRequest);
            return response.HttpStatusCode == System.Net.HttpStatusCode.NoContent;
        }

        public string GetImageUrl(int eventId, string fileExtension)
        {
            return $"{_baseUrl}/events/{eventId}.{fileExtension}";
        }
    }
}
```

### 4. Update Program.cs to Configure Services

```csharp
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Hosting;
using Microsoft.EntityFrameworkCore;
using SchedulingAssistant.Entities;
using SchedulingAssistant.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Add DBEntities context
builder.Services.AddDbContext<DBEntities>(options => {
    string ConnectionString = builder.Configuration["ConnectionStrings:DefaultConnection"] ?? Environment.GetEnvironmentVariable("DISCORD_BOT_CONNECTION_STRING") ?? "";

    if (string.IsNullOrEmpty(ConnectionString))
    {
        string Server = Environment.GetEnvironmentVariable("MYSQL_SERVER") ?? "scheduleBot-db";
        string DB = Environment.GetEnvironmentVariable("MYSQL_DB") ?? "ScheduleBot";
        string User = Environment.GetEnvironmentVariable("MYSQL_USER") ?? "schedulebot";
        string Pass = Environment.GetEnvironmentVariable("MYSQL_USER_PW") ?? "schedulebot";
        ConnectionString = "server=" + Server + ";user=" + User + ";password=" + Pass + ";database=" + DB + ";";
    }

    var serverVersion = new MySqlServerVersion(new Version(8, 0, 26));
    options.UseMySql(ConnectionString, serverVersion);
});

// Add S3 image service
builder.Services.AddSingleton<IS3ImageService, S3ImageService>();

// Configure CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowVRChat", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseCors("AllowVRChat");
app.UseAuthorization();
app.MapControllers();

app.Run();
```

### 5. Add API Key Authentication (Prepared for Future Implementation)

```csharp
using Microsoft.AspNetCore.Authentication;
using Microsoft.Extensions.Options;
using System.Security.Claims;
using System.Text.Encodings.Web;
using System.Threading.Tasks;

namespace SchedulingAssistant.Authentication
{
    public class ApiKeyAuthenticationHandler : AuthenticationHandler<ApiKeyAuthenticationOptions>
    {
        public ApiKeyAuthenticationHandler(
            IOptionsMonitor<ApiKeyAuthenticationOptions> options,
            ILoggerFactory logger,
            UrlEncoder encoder,
            ISystemClock clock) : base(options, logger, encoder, clock)
        {
        }

        protected override Task<AuthenticateResult> HandleAuthenticateAsync()
        {
            // For now, this authentication is disabled and will always succeed
            // In the future, this will be enabled and will check for a valid API key

            var claims = new[] { new Claim(ClaimTypes.Name, "ApiUser") };
            var identity = new ClaimsIdentity(claims, Scheme.Name);
            var principal = new ClaimsPrincipal(identity);
            var ticket = new AuthenticationTicket(principal, Scheme.Name);

            return Task.FromResult(AuthenticateResult.Success(ticket));
        }
    }

    public class ApiKeyAuthenticationOptions : AuthenticationSchemeOptions
    {
        public const string DefaultScheme = "ApiKey";
        public string Scheme => DefaultScheme;
        public string AuthenticationType = DefaultScheme;
    }
}
```

## Error Handling Strategy

1. **Controller Level Handling**:
   - Wrap all operations in try-catch blocks
   - Log errors with sufficient context
   - Return appropriate HTTP status codes
   - Return error messages in a consistent format

2. **Global Exception Handler**:
   - Implement middleware to catch unhandled exceptions
   - Log all unhandled exceptions
   - Return a generic error message to avoid exposing sensitive information

3. **S3 Service Error Handling**:
   - Handle AWS SDK exceptions gracefully
   - Implement retry logic for transient errors
   - Log detailed information about S3 operations

## Testing Plan

### Unit Tests

1. **EventsController Tests**:
   - Test pagination works correctly
   - Test all filter parameters
   - Test error handling scenarios

2. **S3ImageService Tests**:
   - Test image upload functionality
   - Test image URL generation
   - Test error handling for S3 operations

### Integration Tests

1. **API Endpoint Tests**:
   - Test the complete request-response cycle
   - Verify correct data is returned
   - Test with realistic data volumes

2. **S3 Integration Tests**:
   - Test actual uploads to a test S3 bucket
   - Verify CORS configuration works correctly

### Performance Testing

1. **Load Testing**:
   - Test API with concurrent requests
   - Verify acceptable response times under load
   - Identify potential bottlenecks

2. **Bandwidth Testing**:
   - Measure response sizes
   - Optimize payload size for VRChat consumption

## Deployment Considerations

1. **Environment Variables**:
   - `AWS_ACCESS_KEY_ID`: AWS access key
   - `AWS_SECRET_ACCESS_KEY`: AWS secret key
   - `AWS_REGION`: AWS region
   - `S3_BUCKET_NAME`: S3 bucket name
   - `S3_BASE_URL`: Optional custom URL for S3 bucket

2. **Infrastructure Requirements**:
   - Deploy API and database on same VM for low latency
   - Ensure adequate bandwidth for image serving

3. **Monitoring**:
   - Set up logging to capture API usage and errors
   - Monitor S3 bandwidth consumption
   - Set up alerts for high error rates or slow response times

## Documentation

1. **API Documentation**:
   - Setup Swagger/OpenAPI for automatic API documentation
   - Document all parameters and response formats

2. **VRChat Integration Guide**:
   - Create a guide for UDON developers on how to use the API
   - Include sample code for making requests and parsing responses

## Timeline

1. **Phase 1** (1-2 days):
   - Set up Terraform and create S3 bucket
   - Configure access policies and CORS

2. **Phase 2** (2-3 days):
   - Implement the API controller
   - Add S3 service integration

3. **Phase 3** (1-2 days):
   - Write tests and perform testing
   - Optimize for performance

4. **Phase 4** (1 day):
   - Deploy to production
   - Create documentation

## Conclusion

This implementation plan provides a comprehensive roadmap for adding a VRChat UDON-compatible API to the existing scheduling assistant. The solution leverages AWS S3 for image hosting and provides a flexible, paginated API endpoint that can be consumed by UDON scripts in VRChat.
