using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using SchedulingAssistant.Entities;
using System;
using System.Threading.Tasks;

namespace SchedulingAssistant.Services
{
    public interface IDatabaseService
    {
        void ConfigureServices(IServiceCollection services);
        Task MigrateAsync(IServiceProvider serviceProvider);
    }

    public class DatabaseService : IDatabaseService
    {
        private readonly IConfigurationService _configurationService;
        private readonly ILoggerService _loggerService;

        public DatabaseService(IConfigurationService configurationService, ILoggerService loggerService)
        {
            _configurationService = configurationService ?? throw new ArgumentNullException(nameof(configurationService));
            _loggerService = loggerService ?? throw new ArgumentNullException(nameof(loggerService));
            
            _loggerService.LogInformation("DatabaseService initialized");
        }

        public void ConfigureServices(IServiceCollection services)
        {
            if (services == null) throw new ArgumentNullException(nameof(services));
            
            // Add DBEntities context
            services.AddDbContext<DBEntities>(options => 
            {
                string connectionString = _configurationService.GetConnectionString();
                _loggerService.LogInformation($"Configuring database with connection string pattern: server=***;user=***;password=***;database=***");
                
                var serverVersion = new MySqlServerVersion(new Version(8, 0, 26));
                options.UseMySql(connectionString, serverVersion);
            });
            
            _loggerService.LogInformation("Database services configured");
        }

        public async Task MigrateAsync(IServiceProvider serviceProvider)
        {
            if (serviceProvider == null) throw new ArgumentNullException(nameof(serviceProvider));
            
            try 
            {
                using var scope = serviceProvider.CreateScope();
                var db = scope.ServiceProvider.GetRequiredService<DBEntities>();
                
                _loggerService.LogInformation("Applying database migrations...");
                await db.Database.MigrateAsync();
                _loggerService.LogInformation("Migrations applied successfully.");
            }
            catch (Exception ex)
            {
                // Just log the error but don't crash the app
                _loggerService.LogWarning("Error applying migrations. The database might already be up to date.");
                _loggerService.LogError("Migration error details", ex);
            }
        }
    }
} 