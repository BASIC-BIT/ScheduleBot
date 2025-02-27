using Serilog;
using SchedulingAssistant.Utilities;
using System;

namespace SchedulingAssistant.Services
{
    public interface ILoggerService
    {
        void Initialize();
        void LogInformation(string message);
        void LogWarning(string message);
        void LogError(string message, Exception exception = null);
        void LogDebug(string message);
    }

    public class LoggerService : ILoggerService
    {
        public void Initialize()
        {
#if DEBUG
            LoggingUtility.ConfigureLogging(isDebug: true);
#else
            LoggingUtility.ConfigureLogging(isDebug: false);
#endif
            Log.Information("Logger initialized");
        }

        public void LogDebug(string message)
        {
            Log.Debug(message);
        }

        public void LogError(string message, Exception exception = null)
        {
            if (exception != null)
                Log.Error(exception, message);
            else
                Log.Error(message);
        }

        public void LogInformation(string message)
        {
            Log.Information(message);
        }

        public void LogWarning(string message)
        {
            Log.Warning(message);
        }
    }
} 