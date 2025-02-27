using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using SchedulingAssistant.Services;
using System.Threading.Tasks;

namespace SchedulingAssistant
{
    public class Program
    {
        public static async Task Main(string[] args = null)
        {
            // Initialize the application host
            var host = new ApplicationHost();
            
            // Configure and start the application
            await host.RunAsync(args);
        }
    }
}
