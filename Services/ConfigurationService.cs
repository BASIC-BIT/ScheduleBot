using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Abstractions;
using SchedulingAssistant.Utilities;
using System;
using System.IO;

namespace SchedulingAssistant.Services
{
    public interface IConfigurationService
    {
        string GetConnectionString();
        string GetDiscordBotToken();
        bool IsProduction();
        string GetEventImagesBucketUrl();
    }

    public class ConfigurationService : IConfigurationService
    {
        private readonly IConfiguration _configuration;
        private readonly ILogger<ConfigurationService> _logger;
        
        public ConfigurationService(ILogger<ConfigurationService> logger = null)
        {
            _logger = logger ?? NullLogger<ConfigurationService>.Instance;
            
            try
            {
                // Build configuration from appsettings.json and environment variables
                var builder = new ConfigurationBuilder()
                    .SetBasePath(Directory.GetCurrentDirectory())
                    .AddJsonFile("appsettings.json", optional: true, reloadOnChange: true)
                    .AddJsonFile($"appsettings.{EnvironmentConfig.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT", "Production")}.json", optional: true)
                    .AddEnvironmentVariables();
                    
                _configuration = builder.Build();
                
                _logger.LogInformation("ConfigurationService initialized successfully");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error initializing ConfigurationService");
                throw;
            }
        }

        public string GetConnectionString()
        {
            // Get connection string directly from environment variables
            string connectionString = EnvironmentConfig.BuildConnectionString();
            
            if (string.IsNullOrEmpty(connectionString))
            {
                _logger.LogError("No database connection string found in environment variables");
                return null;
            }
            
            _logger.LogDebug("Using connection string from environment variables");
            return connectionString;
        }

        public string GetDiscordBotToken()
        {
            // Get from environment
            string token = EnvironmentConfig.GetEnvironmentVariable("DISCORD_BOT_TOKEN");
            
            if (string.IsNullOrEmpty(token))
            {
                _logger.LogError("Discord bot token not found in environment variables");
            }
            
            return token;
        }

        public bool IsProduction()
        {
            return EnvironmentConfig.IsProduction();
        }
        
        public string GetEventImagesBucketUrl()
        {
            // Get bucket info directly from environment variables - try multiple naming conventions for flexibility
            
            // Try Terraform-style environment variable first
            string bucketName = EnvironmentConfig.GetEnvironmentVariable("EVENT_IMAGES_BUCKET_NAME");
            
            // Fall back to Docker-style environment variable if needed
            if (string.IsNullOrEmpty(bucketName))
            {
                bucketName = EnvironmentConfig.GetEnvironmentVariable("AWS_BUCKET_NAME");
            }
            
            if (!string.IsNullOrEmpty(bucketName))
            {
                string region = EnvironmentConfig.GetEnvironmentVariable("AWS_REGION", "us-east-1");
                
                // Create the S3 bucket URL in the standard format
                string bucketUrl = $"https://{bucketName}.s3.{region}.amazonaws.com";
                _logger.LogDebug("Using S3 bucket URL constructed from environment variables: {BucketUrl}", bucketUrl);
                return bucketUrl;
            }
            
            _logger.LogError("Event images bucket name not found in environment variables");
            return null;
        }
    }
} 