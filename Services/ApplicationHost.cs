using Microsoft.Extensions.DependencyInjection;
using Serilog;
using System;
using System.Threading.Tasks;

namespace SchedulingAssistant.Services
{
    public class ApplicationHost
    {
        private readonly ServiceProvider _serviceProvider;
        
        public ApplicationHost()
        {
            try
            {
                // Initialize the service collection
                var services = new ServiceCollection();
                
                // Register services
                ConfigureServices(services);
                
                // Build the service provider
                _serviceProvider = services.BuildServiceProvider();
                
                Log.Information("ApplicationHost initialized successfully");
            }
            catch (Exception ex)
            {
                // Use direct Serilog call since the logger service isn't available yet
                Log.Fatal(ex, "Failed to initialize ApplicationHost");
                throw;
            }
        }
        
        private void ConfigureServices(IServiceCollection services)
        {
            if (services == null) throw new ArgumentNullException(nameof(services));
            
            try
            {
                Log.Information("Registering services...");
                
                // Register core services
                services.AddSingleton<ILoggerService, LoggerService>();
                services.AddSingleton<IConfigurationService, ConfigurationService>();
                
                // Database service depends on configuration and logger
                services.AddSingleton<IDatabaseService>(provider => 
                    new DatabaseService(
                        provider.GetRequiredService<IConfigurationService>(),
                        provider.GetRequiredService<ILoggerService>()
                    )
                );
                
                // Register application services
                services.AddSingleton<IWebApiService>(provider => 
                    new WebApiService(
                        provider.GetRequiredService<ILoggerService>(),
                        provider.GetRequiredService<IConfigurationService>(),
                        provider.GetRequiredService<IDatabaseService>()
                    )
                );
                
                services.AddSingleton<IDiscordBotService>(provider => 
                    new DiscordBotService(
                        provider.GetRequiredService<ILoggerService>(),
                        provider.GetRequiredService<IConfigurationService>()
                    )
                );
                
                Log.Information("Services registered successfully");
            }
            catch (Exception ex)
            {
                Log.Error(ex, "Failed to register services");
                throw;
            }
        }
        
        public async Task RunAsync(string[] args)
        {
            if (args == null) args = Array.Empty<string>();
            
            try
            {
                // Initialize logging
                var loggerService = _serviceProvider.GetRequiredService<ILoggerService>();
                loggerService.Initialize();
                loggerService.LogInformation($"Application starting with args: [{string.Join(", ", args)}]");
                
                // Parse command line arguments
                bool webApiOnly = args.Length > 0 && args[0] == "--webapi";
                bool botOnly = args.Length > 0 && args[0] == "--bot";
                
                if (webApiOnly)
                    loggerService.LogInformation("Running in Web API only mode");
                else if (botOnly)
                    loggerService.LogInformation("Running in Discord Bot only mode");
                else
                    loggerService.LogInformation("Running in combined mode (both Web API and Discord Bot)");
                
                // Start services based on command-line arguments
                if (!botOnly)
                {
                    loggerService.LogInformation("Starting Web API service...");
                    var webApiService = _serviceProvider.GetRequiredService<IWebApiService>();
                    await webApiService.StartAsync(args);
                }
                
                if (!webApiOnly)
                {
                    loggerService.LogInformation("Starting Discord Bot service...");
                    var discordBotService = _serviceProvider.GetRequiredService<IDiscordBotService>();
                    await discordBotService.StartAsync();
                }
                
                loggerService.LogInformation("All services started successfully, application is now running");
                
                // Keep the application alive
                await Task.Delay(-1);
            }
            catch (Exception ex)
            {
                Log.Fatal(ex, "Fatal error in application host");
                throw;
            }
        }
    }
} 