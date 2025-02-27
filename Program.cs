using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.EntityFrameworkCore;
using Serilog;
using SchedulingAssistant.Entities;
using SchedulingAssistant.Services;
using SchedulingAssistant.Authentication;
using System;
using System.Threading.Tasks;

namespace SchedulingAssistant
{
    internal class Program
    {
        public static async Task Main(string[] args = null)
        {
            // Check if only web API mode is requested (for development/testing)
            bool webApiOnly = args != null && args.Length > 0 && args[0] == "--webapi";
            bool botOnly = args != null && args.Length > 0 && args[0] == "--bot";

            // Configure logging
#if DEBUG
            Log.Logger = new LoggerConfiguration()
                             .WriteTo.File("Logs/schedulebot.log", rollingInterval: RollingInterval.Day)
                             .WriteTo.Console(outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff} [{SourceContext}] [{Level}] {Message}{NewLine}{Exception}")
                             .MinimumLevel.Debug()
                             .CreateLogger();
#else
            Log.Logger = new LoggerConfiguration()
                             .WriteTo.File("Logs/schedulebot.log", rollingInterval: RollingInterval.Day)
                             .WriteTo.Console(outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff} [{SourceContext}] [{Level}] {Message}{NewLine}{Exception}")
                             .MinimumLevel.Information()
                             .CreateLogger();
#endif

            // Start Web API if not bot-only mode
            if (!botOnly)
            {
                Log.Information("Starting Web API...");
                
                // Run the Web API as a background task
                Task webApiTask = Task.Run(() => StartWebApi(args));
            }

            // Start Discord bot if not web-api-only mode
            if (!webApiOnly)
            {
                Log.Information("Starting Discord Bot...");
                
                // Run the Discord bot with exception handling and retries
                while (true)
                {
                    try
                    {
                        var KEY = Environment.GetEnvironmentVariable("DISCORD_BOT_TOKEN") ?? "";
                        
                        // Skip Discord bot if token is empty or set to 'test_token'
                        if (string.IsNullOrWhiteSpace(KEY) || KEY == "test_token")
                        {
                            Log.Warning("Discord bot token is empty or set to test_token. Skipping Discord bot initialization.");
                            break;
                        }
                        
                        await new Bot().StartAsync(KEY);
                    }
                    catch (Exception ex)
                    {
                        Log.Error(ex, "Discord bot encountered an error");
                    }
                    
                    // Wait before restart attempt
                    await Task.Delay(5000);
                }
            }
            
            // Keep the application alive
            await Task.Delay(-1);
        }

        private static void StartWebApi(string[] args)
        {
            try
            {
                var builder = WebApplication.CreateBuilder(args);

                // Add services to the container.
                builder.Services.AddControllers();
                builder.Services.AddEndpointsApiExplorer();
                builder.Services.AddSwaggerGen();

                // Add DBEntities context
                builder.Services.AddDbContext<DBEntities>(options => {
                    string ConnectionString = builder.Configuration["ConnectionStrings:DefaultConnection"] ?? Environment.GetEnvironmentVariable("DISCORD_BOT_CONNECTION_STRING") ?? "";

                    if (string.IsNullOrEmpty(ConnectionString))
                    {
                        string Server = Environment.GetEnvironmentVariable("MYSQL_SERVER") ?? "scheduleBot-db";
                        string DB = Environment.GetEnvironmentVariable("MYSQL_DB") ?? "ScheduleBot";
                        string User = Environment.GetEnvironmentVariable("MYSQL_USER") ?? "schedulebot";
                        string Pass = Environment.GetEnvironmentVariable("MYSQL_USER_PW") ?? "schedulebot";
                        ConnectionString = "server=" + Server + ";user=" + User + ";password=" + Pass + ";database=" + DB + ";";
                    }

                    var serverVersion = new MySqlServerVersion(new Version(8, 0, 26));
                    options.UseMySql(ConnectionString, serverVersion);
                });

                // Add S3 image service
                builder.Services.AddSingleton<IS3ImageService, S3ImageService>();

                // Configure AWS services
                builder.Services.AddAWSService<Amazon.S3.IAmazonS3>();

                // Configure API Key Authentication (prepared for future implementation)
                builder.Services.AddAuthentication(options =>
                {
                    options.DefaultAuthenticateScheme = ApiKeyAuthenticationOptions.DefaultScheme;
                    options.DefaultChallengeScheme = ApiKeyAuthenticationOptions.DefaultScheme;
                })
                .AddScheme<ApiKeyAuthenticationOptions, ApiKeyAuthenticationHandler>(
                    ApiKeyAuthenticationOptions.DefaultScheme, 
                    options => { });

                // Configure CORS
                builder.Services.AddCors(options =>
                {
                    options.AddPolicy("AllowVRChat", policy =>
                    {
                        policy.AllowAnyOrigin()
                              .AllowAnyMethod()
                              .AllowAnyHeader();
                    });
                });

                var app = builder.Build();

                // Apply migrations with error handling
                using (var scope = app.Services.CreateScope())
                {
                    try 
                    {
                        var db = scope.ServiceProvider.GetRequiredService<DBEntities>();
                        Log.Information("Applying database migrations...");
                        db.Database.Migrate();
                        Log.Information("Migrations applied successfully.");
                    }
                    catch (Exception ex)
                    {
                        // Just log the error but don't crash the app
                        Log.Warning(ex, "Error applying migrations. The database might already be up to date.");
                    }
                }

                // Configure the HTTP request pipeline.
                if (app.Environment.IsDevelopment())
                {
                    app.UseSwagger();
                    app.UseSwaggerUI();
                }

                app.UseHttpsRedirection();
                app.UseCors("AllowVRChat");
                app.UseAuthorization();
                app.MapControllers();

                app.Run();
            }
            catch (Exception ex)
            {
                Log.Error(ex, "Web API encountered an error");
            }
        }
    }
}
