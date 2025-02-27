using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using SchedulingAssistant.Services;
using System;
using System.Threading.Tasks;
using Serilog;

namespace SchedulingAssistant
{
    public class Program
    {
        public static async Task Main(string[] args = null)
        {
            // Initialize logging first for global exception handling
            Log.Logger = new LoggerConfiguration()
                .WriteTo.Console()
                .MinimumLevel.Information()
                .CreateLogger();

            try
            {
                Log.Information("Starting SchedulingAssistant application");
                
                // Set up global exception handling
                AppDomain.CurrentDomain.UnhandledException += (sender, eventArgs) =>
                {
                    Log.Error(eventArgs.ExceptionObject as Exception, "Unhandled application exception");
                };
                
                // Initialize the application host
                var host = new ApplicationHost();
                
                // Configure and start the application
                await host.RunAsync(args);
            }
            catch (Exception ex)
            {
                Log.Fatal(ex, "Application terminated unexpectedly");
            }
            finally
            {
                Log.CloseAndFlush();
            }
        }
    }
}
