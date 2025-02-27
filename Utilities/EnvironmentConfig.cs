using System;

namespace SchedulingAssistant.Utilities
{
    /// <summary>
    /// Utility class for handling environment variables and configuration
    /// </summary>
    public static class EnvironmentConfig
    {
        /// <summary>
        /// Gets an environment variable with a fallback value if not found
        /// </summary>
        public static string GetEnvironmentVariable(string name, string defaultValue = "")
        {
            return Environment.GetEnvironmentVariable(name) ?? defaultValue;
        }
        
        /// <summary>
        /// Builds a MySQL connection string from environment variables or uses defaults
        /// </summary>
        public static string BuildConnectionString()
        {
            string connectionString = GetEnvironmentVariable("DISCORD_BOT_CONNECTION_STRING");

            if (string.IsNullOrEmpty(connectionString))
            {
                string server = GetEnvironmentVariable("MYSQL_SERVER", "scheduleBot-db");
                string db = GetEnvironmentVariable("MYSQL_DB", "ScheduleBot");
                string user = GetEnvironmentVariable("MYSQL_USER", "schedulebot");
                string pass = GetEnvironmentVariable("MYSQL_USER_PW", "schedulebot");
                connectionString = $"server={server};user={user};password={pass};database={db};";
            }

            return connectionString;
        }
        
        /// <summary>
        /// Determines if the current environment is production
        /// </summary>
        public static bool IsProduction()
        {
            var environment = GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT");
            return string.IsNullOrEmpty(environment) || 
                   environment.Equals("Production", StringComparison.OrdinalIgnoreCase);
        }
    }
} 