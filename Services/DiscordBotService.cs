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
            
            // Run the Discord bot with exception handling and retries
            while (true)
            {
                try
                {
                    var token = _configurationService.GetDiscordBotToken();
                    _loggerService.LogDebug($"Discord bot token retrieved, length: {token?.Length ?? 0}");
                    
                    // Skip Discord bot if token is empty or set to 'test_token'
                    if (string.IsNullOrWhiteSpace(token) || token == "test_token")
                    {
                        _loggerService.LogWarning("Discord bot token is empty or set to test_token. Skipping Discord bot initialization.");
                        break;
                    }
                    
                    _loggerService.LogInformation("Initializing Discord bot with valid token");
                    await new Bot().StartAsync(token);
                }
                catch (Exception ex)
                {
                    _loggerService.LogError("Discord bot encountered an error", ex);
                    _loggerService.LogInformation("Waiting before retry...");
                }
                
                // Wait before restart attempt
                await Task.Delay(5000);
            }
        }
    }
} 