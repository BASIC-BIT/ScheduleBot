using Microsoft.Extensions.Configuration;
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
    }

    public class ConfigurationService : IConfigurationService
    {
        private readonly IConfiguration _configuration;
        
        public ConfigurationService()
        {
            // Build configuration from appsettings.json and environment variables
            var builder = new ConfigurationBuilder()
                .SetBasePath(Directory.GetCurrentDirectory())
                .AddJsonFile("appsettings.json", optional: true, reloadOnChange: true)
                .AddJsonFile($"appsettings.{EnvironmentConfig.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT", "Production")}.json", optional: true)
                .AddEnvironmentVariables();
                
            _configuration = builder.Build();
        }

        public string GetConnectionString()
        {
            string connectionString = _configuration["ConnectionStrings:DefaultConnection"];
            
            if (string.IsNullOrEmpty(connectionString)) 
            {
                connectionString = EnvironmentConfig.BuildConnectionString();
            }
            
            return connectionString;
        }

        public string GetDiscordBotToken()
        {
            return EnvironmentConfig.GetEnvironmentVariable("DISCORD_BOT_TOKEN");
        }

        public bool IsProduction()
        {
            return EnvironmentConfig.IsProduction();
        }
    }
} 