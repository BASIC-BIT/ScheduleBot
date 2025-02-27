using Serilog;
using Serilog.Events;

namespace SchedulingAssistant.Utilities
{
    /// <summary>
    /// Utility class for logging configuration
    /// </summary>
    public static class LoggingUtility
    {
        /// <summary>
        /// Configures and initializes the Serilog logger
        /// </summary>
        public static void ConfigureLogging(bool isDebug = false)
        {
            var loggerConfig = new LoggerConfiguration()
                .WriteTo.File("Logs/schedulebot.log", rollingInterval: RollingInterval.Day)
                .WriteTo.Console(outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff} [{SourceContext}] [{Level}] {Message}{NewLine}{Exception}");
                
            if (isDebug)
            {
                loggerConfig.MinimumLevel.Debug();
            }
            else
            {
                loggerConfig.MinimumLevel.Information();
            }
            
            Log.Logger = loggerConfig.CreateLogger();
        }
    }
} 