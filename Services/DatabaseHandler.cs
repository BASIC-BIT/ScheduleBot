using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using SchedulingAssistant.Entities;
using System;
using System.IO;
using System.Threading.Tasks;
using DSharpPlus;

namespace SchedulingAssistant.Services
{
    internal class DatabaseHandler
    {
        private readonly IServiceProvider _services;
        private readonly ILogger<DatabaseHandler> _logger;
        private readonly DiscordClient _client;

        public DatabaseHandler(IServiceProvider services)
        {
            _services = services;
            _logger = _services.GetRequiredService<ILogger<DatabaseHandler>>();
            _client = _services.GetRequiredService<DiscordClient>();
        }

        public async Task Initalize()
        {
            _logger.LogInformation("Initializing Database");
            try
            {
                using var db = new DBEntities();
                await db.Database.MigrateAsync();
                
                // Execute the ticket system tables SQL script
                await InitializeTicketSystemTables();
                
                _logger.LogInformation("Database Initialized");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error initializing database");
                throw;
            }
        }
        
        private async Task InitializeTicketSystemTables()
        {
            try
            {
                _logger.LogInformation("Initializing Ticket System Tables");
                
                // Read the SQL script
                string sqlScript = await File.ReadAllTextAsync("db/ticket_system_tables.sql");
                
                // Split the script into individual commands
                string[] commands = sqlScript.Split(new[] { ";" }, StringSplitOptions.RemoveEmptyEntries);
                
                using var db = new DBEntities();
                using var connection = db.Database.GetDbConnection();
                await connection.OpenAsync();
                
                using var command = connection.CreateCommand();
                
                // Execute each command
                foreach (string commandText in commands)
                {
                    if (string.IsNullOrWhiteSpace(commandText))
                        continue;
                    
                    command.CommandText = commandText;
                    await command.ExecuteNonQueryAsync();
                }
                
                _logger.LogInformation("Ticket System Tables Initialized");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error initializing ticket system tables");
                throw;
            }
        }
    }
}
