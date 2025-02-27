using System;
using System.Threading.Tasks;

namespace SchedulingAssistant.Services
{
    public interface IDiscordBotService
    {
        Task StartAsync();
    }

    public class DiscordBotService : IDiscordBotService
    {
        private readonly ILoggerService _loggerService;
        private readonly IConfigurationService _configurationService;
        
        public DiscordBotService(
            ILoggerService loggerService,
            IConfigurationService configurationService)
        {
            _loggerService = loggerService ?? throw new ArgumentNullException(nameof(loggerService));
            _configurationService = configurationService ?? throw new ArgumentNullException(nameof(configurationService));
            
            _loggerService.LogInformation("DiscordBotService initialized");
        }
        
        public async Task StartAsync()
        {
            _loggerService.LogInformation("Starting Discord Bot...");
            
            // Try to get the token upfront to diagnose any issues
            var initialToken = _configurationService.GetDiscordBotToken();
            _loggerService.LogInformation($"Initial Discord bot token check: {(string.IsNullOrEmpty(initialToken) ? "Not found" : $"Found (length: {initialToken.Length})")}");
            
            // Run the Discord bot with exception handling and retries
            int retryCount = 0;
            const int maxRetries = 3;
            
            while (retryCount < maxRetries)
            {
                try
                {
                    var token = _configurationService.GetDiscordBotToken();
                    _loggerService.LogDebug($"Discord bot token retrieved, length: {token?.Length ?? 0}");
                    
                    // Skip Discord bot if token is empty or set to 'test_token'
                    if (string.IsNullOrWhiteSpace(token) || token == "test_token")
                    {
                        _loggerService.LogWarning("Discord bot token is empty or set to test_token. Skipping Discord bot initialization.");
                        
                        // Additional diagnostics for troubleshooting
                        _loggerService.LogWarning("Environment variable access issue may be preventing token retrieval.");
                        
                        // In production, break to avoid retries for missing token
                        if (_configurationService.IsProduction())
                        {
                            break;
                        }
                        
                        // In development, try a few times in case it's a timing issue
                        retryCount++;
                        _loggerService.LogInformation($"Retry attempt {retryCount} of {maxRetries}");
                        await Task.Delay(5000);
                        continue;
                    }
                    
                    _loggerService.LogInformation("Initializing Discord bot with valid token");
                    await new Bot().StartAsync(token);
                    
                    // If we get here, the bot started successfully
                    _loggerService.LogInformation("Discord bot started successfully");
                    break;
                }
                catch (Exception ex)
                {
                    _loggerService.LogError("Discord bot encountered an error", ex);
                    _loggerService.LogInformation("Waiting before retry...");
                    retryCount++;
                    
                    if (retryCount >= maxRetries)
                    {
                        _loggerService.LogError("Maximum retry attempts reached. Discord bot will not be started.");
                        break;
                    }
                    
                    // Wait before restart attempt
                    await Task.Delay(5000);
                }
            }
        }
    }
} 