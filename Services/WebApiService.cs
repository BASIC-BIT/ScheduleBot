using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using SchedulingAssistant.Authentication;
using SchedulingAssistant.Services;
using System;
using System.Threading.Tasks;

namespace SchedulingAssistant.Services
{
    public interface IWebApiService
    {
        Task StartAsync(string[] args);
    }

    public class WebApiService : IWebApiService
    {
        private readonly ILoggerService _loggerService;
        private readonly IConfigurationService _configurationService;
        private readonly IDatabaseService _databaseService;

        public WebApiService(
            ILoggerService loggerService,
            IConfigurationService configurationService,
            IDatabaseService databaseService)
        {
            _loggerService = loggerService ?? throw new ArgumentNullException(nameof(loggerService));
            _configurationService = configurationService ?? throw new ArgumentNullException(nameof(configurationService));
            _databaseService = databaseService ?? throw new ArgumentNullException(nameof(databaseService));
            
            _loggerService.LogInformation("WebApiService initialized");
        }

        public async Task StartAsync(string[] args)
        {
            try
            {
                _loggerService.LogInformation("Starting Web API...");
                
                // Run the Web API in a background task to not block the main thread
                await Task.Run(() => BuildAndRunWebApi(args));
            }
            catch (Exception ex)
            {
                _loggerService.LogError("Web API encountered an error", ex);
                throw; // Rethrow to ensure the error propagates to the host
            }
        }

        private void BuildAndRunWebApi(string[] args)
        {
            _loggerService.LogInformation("Building Web API...");
            var builder = WebApplication.CreateBuilder(args);

            // Add services to the container
            ConfigureServices(builder.Services);

            _loggerService.LogInformation("Building Web application...");
            var app = builder.Build();

            // Apply migrations
            _loggerService.LogInformation("Applying database migrations...");
            _databaseService.MigrateAsync(app.Services).GetAwaiter().GetResult();

            // Configure the HTTP request pipeline
            ConfigureMiddleware(app);

            // Start the web server
            _loggerService.LogInformation("Starting Web server...");
            app.Run();
        }

        private void ConfigureServices(IServiceCollection services)
        {
            _loggerService.LogInformation("Configuring Web API services...");
            
            // Add controllers and API explorer
            services.AddControllers();
            services.AddEndpointsApiExplorer();
            services.AddSwaggerGen();

            // Configure database
            _databaseService.ConfigureServices(services);

            // Add S3 image service
            services.AddSingleton<IS3ImageService, S3ImageService>();

            // Configure AWS services
            services.AddAWSService<Amazon.S3.IAmazonS3>();

            // Configure API Key Authentication
            services.AddAuthentication(options =>
            {
                options.DefaultAuthenticateScheme = ApiKeyAuthenticationOptions.DefaultScheme;
                options.DefaultChallengeScheme = ApiKeyAuthenticationOptions.DefaultScheme;
            })
            .AddScheme<ApiKeyAuthenticationOptions, ApiKeyAuthenticationHandler>(
                ApiKeyAuthenticationOptions.DefaultScheme, 
                options => { });

            // Configure CORS
            services.AddCors(options =>
            {
                options.AddPolicy("AllowVRChat", policy =>
                {
                    policy.AllowAnyOrigin()
                          .AllowAnyMethod()
                          .AllowAnyHeader();
                });
            });
            
            _loggerService.LogInformation("Web API services configured successfully");
        }

        private void ConfigureMiddleware(WebApplication app)
        {
            _loggerService.LogInformation("Configuring Web API middleware...");
            
            // Configure development-specific middleware
            if (app.Environment.IsDevelopment())
            {
                _loggerService.LogInformation("Development environment detected, enabling Swagger");
                app.UseSwagger();
                app.UseSwaggerUI();
            }
            else
            {
                // Temporarily disabled HTTPS redirection to avoid certificate issues
                _loggerService.LogInformation("Production environment detected, but HTTPS redirection is temporarily disabled");
                // app.UseHttpsRedirection();  // Commented out to avoid certificate issues
            }

            // Configure standard middleware
            app.UseCors("AllowVRChat");
            app.UseAuthorization();
            app.MapControllers();
            
            _loggerService.LogInformation("Web API middleware configured successfully");
        }
    }
} 