using CsvHelper;
using DSharpPlus;
using DSharpPlus.Entities;
using DSharpPlus.SlashCommands;
using DSharpPlus.SlashCommands.Attributes;
using SchedulingAssistant.Entities;
using SchedulingAssistant.Models;
using System.Globalization;
using System.Net;
using System.Reflection;
using System.Text.RegularExpressions;


namespace SchedulingAssistant.Commands
{
    public class Admin : ApplicationCommandModule
    {
        [SlashCommand("refesh", "Refreshes the UI of the schedules that haven't ended. Purely to fix the UI.")]
        [SlashRequireUserPermissions(Permissions.ManageMessages)]
        public async Task Refresh(InteractionContext ctx)
        {
            await ctx.CreateResponseAsync($"Working on it!", true);

            using (var db = new DBEntities())
            {
                ServerSetting? Server = db.ServerSettings.FirstOrDefault(x => x.ServerId == ctx.Guild.Id);

                if (Server == null)
                {
                    await ctx.CreateResponseAsync($"No channel set. Use setEventChannel.", true);
                    return;
                }

                IEnumerable<DiscordChannel> Channels = await ctx.Guild.GetChannelsAsync();
                DiscordChannel? Channel = Channels.FirstOrDefault(x => x.Id == Server.ChannelId);

                if (Channel == null)
                {
                    await ctx.CreateResponseAsync($"No channel set. Use setEventChannel.", true);
                    return;
                }

                var schedules = db.Schedules.Where(x => (x.ServerId == ctx.Guild.Id) && (x.HasEnded == false)).ToList();

                foreach (var schedule in schedules)
                {
                    try
                    {
                        DiscordMessage? message = await Channel.GetMessageAsync(schedule.EventId);
                        if (message != null)
                        {
                            await message.ModifyAsync(schedule.BuildMessage());
                        }
                    }
                    catch (Exception ex)
                    {

                    }
                }
            }
        }

        [SlashCommand("setEventChannel", "Set Channel for Events.")]
        [SlashRequireUserPermissions(Permissions.ManageMessages)]
        public async Task SetEventChannel(InteractionContext ctx, [Option("Channel", "Channel for bot to post events", false)] DiscordChannel Channel)
        {
            using (var db = new DBEntities())
            {
                var ServerSetting = db.ServerSettings.FirstOrDefault(x => x.ServerId == ctx.Guild.Id) ?? new ServerSetting(ctx.Guild.Id);
                ServerSetting.ChannelId = Channel.Id;
                
                try
                {
                    await ServerSetting.Update();
                    await ctx.CreateResponseAsync($"Now posting events in {Channel.Mention}", true);
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex);
                    await ctx.CreateResponseAsync($"There was an error updating your server setting", true);
                    throw ex;
                }
            }
        }

        [SlashCommand("getAttendanceReport", "Gets attendance report for a date range.")]
        [SlashRequireUserPermissions(Permissions.ManageMessages)]
        public async Task GetAttendanceReport(
            InteractionContext ctx,
            [Option("StartDate", "Date to start the report", false)] string StartDateForEvent,
            [Option("EndDate", "Date to end the report", false)] string EndDateForEvent
        )
        {
            DateTime? StartTime = null;
            DateTime? EndTime = null;

            try
            {
                StartTime = DateTime.Parse(StartDateForEvent);
            }
            catch
            {
                await ctx.CreateResponseAsync($"Not a valid Start Time Format", true);
                return;
            }
            try
            {
                EndTime = DateTime.Parse(EndDateForEvent);
            }
            catch
            {
                await ctx.CreateResponseAsync($"Not a valid End Time Format", true);
                return;
            }

            await ctx.CreateResponseAsync($"Getting your report. Hold tight...", true);

            try
            {
                using (var db = new DBEntities())
                {
                    var Schedules = db.Schedules.Where(x => x.HasEnded == true && x.StartTime >= StartTime && x.EndTime <= EndTime).ToList();
                    List<int> ScheduleIds = Schedules.Select(x => x.Id).ToList();
                    var Attendees = db.Attenants.Where(x => ScheduleIds.Contains(x.ScheduleId)).ToList();

                    var dm = await ctx.Member.CreateDmChannelAsync();
                    var message = await dm.SendMessageAsync("Getting your report. Hold tight...");
                    DiscordMessageBuilder DMB = new DiscordMessageBuilder();

                    List<ReportOutput> Output = new();

                    foreach (var s in Schedules)
                    {
                        foreach (var a in Attendees.Where(x => x.ScheduleId == s.Id))
                        {
                            Output.Add(new()
                            {
                                EventId = s.EventId,
                                Date = s.StartTime,
                                Description = s.EventDescription,
                                Name = s.EventTitle,
                                UserId = a.UserId,
                                UserName = a.Name
                            });
                        }
                    }

                    if (Output.Count == 0)
                    {
                        DMB.WithContent("There are no events in that time range");
                        await message.ModifyAsync(DMB);

                    }
                    else
                    {
                        DMB.WithContent("Here you go!");
                        string filePath = $"{ctx.InteractionId}.csv";

                        //string csv = String.Join(",", Output);
                        //FileStream fWrite = new FileStream(filePath, FileMode.OpenOrCreate, FileAccess.ReadWrite, FileShare.ReadWrite);

                        //byte[] writeArr = Encoding.UTF8.GetBytes(csv); 
                        //await fWrite.WriteAsync(writeArr, 0, csv.Length);
                        //fWrite.Close();

                        using (var writer = new StreamWriter(filePath))
                        using (var csvF = new CsvWriter(writer, CultureInfo.InvariantCulture))
                        {
                            csvF.WriteRecords(Output);
                        }

                        using (var fs = new FileStream(filePath, FileMode.Open, FileAccess.Read))
                        {
                            var dmb = new DiscordMessageBuilder()
                                .WithContent("Here is your report!")
                                .AddFile(fs, false);
                            await message.ModifyAsync(dmb);
                        }


                        if (File.Exists(filePath))
                        {
                            File.Delete(filePath);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                await ctx.CreateResponseAsync($"There was an error getting your report", true);
                throw ex;
            }
        }

        [SlashCommand("version", "Get Schedulebot Version.")]
        [SlashRequireUserPermissions(Permissions.ManageMessages)]
        public async Task GetVersion(InteractionContext ctx)
        {
            await ctx.CreateResponseAsync(@$"I am running version {Assembly.GetEntryAssembly().GetName().Version}", true);
        }

        [SlashCommand("restartEvent", "Restarts Event.")]
        [SlashRequireUserPermissions(Permissions.ManageMessages)]
        public async Task RestartEvent(
            InteractionContext ctx,
            [Option("EventId", "The ID of the Event", false)] string MessageId
        )
        {
            Regex R = new Regex(@"([0-9]*)");

            if (!R.IsMatch(MessageId))
            {
                await ctx.CreateResponseAsync($"Not a valid message Id", true);
                return;
            }

            using (var db = new DBEntities())
            {
                var ServerSetting = db.ServerSettings.FirstOrDefault(x => x.ServerId == ctx.Guild.Id) ?? new ServerSetting(ctx.Guild.Id);
                if (ServerSetting.ChannelId == null)
                {
                    await ctx.CreateResponseAsync($"No Event Channel Set. Have admin set channel using /setEventChannel", true);
                    return;
                }

                Schedule? Schedule = null;

                try
                {
                    ulong EventId = ulong.Parse(R.Match(MessageId).Value);

                    Schedule = db.Schedules.FirstOrDefault(x => x.EventId == EventId);
                    if (Schedule == null)
                    {
                        await ctx.CreateResponseAsync($"Unable to get an event of that Id", true);
                        return;
                    }
                }
                catch
                {
                    await ctx.CreateResponseAsync($"Unable to get an event of that Id", true);
                    return;
                }
                DiscordRole? DiscordRole = null;

                if (Schedule.HasEnded == true)
                {
                    var BaseRoleName = String.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISCORD_EVENT_ROLE_PREFIX")) ? "EventRole" : Environment.GetEnvironmentVariable("DISCORD_EVENT_ROLE_PREFIX");
                    string RoleName;
                    int i = 0;
                    do
                    {
                        i++;
                        RoleName = $"{BaseRoleName}-{i}";
                    }
                    while (ctx.Guild.Roles.Values.FirstOrDefault(x => x.Name == RoleName) != null);

                    DiscordRole = await ctx.Guild.CreateRoleAsync(RoleName, mentionable: true);
                }
                else
                {
                    DiscordRole = ctx.Guild.Roles.Values.FirstOrDefault(x => x.Id == Schedule.RoleId);
                }


                if (DiscordRole == null)
                {
                    await ctx.CreateResponseAsync($"Unable to create role. Check Permissions as this role already exists.", true);
                    return;
                }

                Schedule.RoleId = DiscordRole.Id;
                Schedule.IsActive = false;
                Schedule.HasEnded = false;

                try
                {
                    DiscordMessageBuilder MBuilder = Schedule.BuildMessage();
                    try
                    {
                        var Message = await ctx.Guild.GetChannel((ulong)ServerSetting.ChannelId).GetMessageAsync(Schedule.EventId);
                        await Message.ModifyAsync(MBuilder);
                        await Schedule.Update();


                        List<Attendence> Attendees = db.Attenants.Where(x => x.ScheduleId == Schedule.Id).ToList();
                        foreach (var User in Attendees)
                        {
                            DiscordMember? DM = await ctx.Guild.GetMemberAsync(User.UserId);
                            if (DM != null)
                            {
                                await DM.GrantRoleAsync(DiscordRole);
                            }
                        }
                        await ctx.CreateResponseAsync($"Here you go!", true);
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine(ex);
                        await ctx.CreateResponseAsync($"There was an error updating your event.", true);
                    }
                }
                catch
                {
                    await DiscordRole.DeleteAsync();
                    await ctx.CreateResponseAsync($"There was an error restarting your event.", true);
                }
            }
        }

        [SlashCommand("Event", "Post Event.")]
        [SlashRequireUserPermissions(Permissions.ManageMessages)]
        public async Task PostEvent(
            InteractionContext ctx,
            [Option("Name", "Name of the event", false)] string EventName,
            [Option("Description", "Event Detials", false)] string Description,
            [Option("EventStart", "When the event occurs", false)] string EventStart,
            [Option("Duration", "How many hours till this event ends?", false)] double EventEnd,
            [Option("ProfileURL", "VRC Profile User Hosting Event", false)] string HostURL,
            [Option("World", "Link to world", false)] string WorldLink = "",
            [Option("Host", "User Hosting Event", false)] DiscordUser Host = null,
            [Option("ImageURL", "Image URL", false)] string Image = null
            )
        {

            using (var db = new DBEntities())
            {
                var ServerSetting = db.ServerSettings.FirstOrDefault(x => x.ServerId == ctx.Guild.Id) ?? new ServerSetting(ctx.Guild.Id);
                if (ServerSetting.ChannelId == null)
                {
                    await ctx.CreateResponseAsync($"No Event Channel Set. Have admin set channel using /setEventChannel", true);
                    return;
                }
                DateTime? StartTime = null;
                DateTime? EndTime = null;

                try
                {
                    if (TimeCode.IsMatch(EventStart))
                    {
                        long unixTimeStamp = long.Parse(TimeCode.Match(EventStart).Groups[1].Value);
                        System.DateTime dtDateTime = new DateTime(1970, 1, 1, 0, 0, 0, 0, System.DateTimeKind.Utc);
                        StartTime = dtDateTime.AddSeconds(unixTimeStamp);
                    }
                    else
                    {
                        StartTime = DateTime.Parse(EventStart);
                    }
                }
                catch
                {
                    await ctx.CreateResponseAsync($"Not a valid Start Time Format", true);
                    return;
                }
                try
                {
                    EndTime = StartTime.Value.AddHours(EventEnd);
                }
                catch
                {
                    await ctx.CreateResponseAsync($"Not a valid End Time Format", true);
                    return;
                }

                try
                {
                    Regex URL = new Regex(@"^http:\/\/|^https:\/\/");
                    if (!URL.IsMatch(HostURL))
                    {
                        await ctx.CreateResponseAsync(@$"Not a valid Host URL. Ensure link starts with http:// or https://", true);
                        return;
                    }
                    if (!string.IsNullOrEmpty(WorldLink))
                    {
                        if (!URL.IsMatch(WorldLink))
                        {
                            await ctx.CreateResponseAsync(@$"Not a valid World Link. Ensure link starts with http:// or https://", true);
                            return;
                        }
                    }
                    if (!string.IsNullOrEmpty(Image))
                    {
                        if (!URL.IsMatch(Image))
                        {
                            await ctx.CreateResponseAsync(@$"Not a valid Image Link. Ensure link starts with http:// or https://", true);
                            return;
                        }
                    }

                }
                catch
                {
                    await ctx.CreateResponseAsync(@$"Not a valid Image, Host or World URL. Ensure link starts with http:// or https://", true);
                    return;
                }



                var BaseRoleName = String.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISCORD_EVENT_ROLE_PREFIX")) ? "EventRole" : Environment.GetEnvironmentVariable("DISCORD_EVENT_ROLE_PREFIX");
                string RoleName;
                int i = 0;
                do
                {
                    i++;
                    RoleName = $"{BaseRoleName}-{i}";
                }
                while (ctx.Guild.Roles.Values.FirstOrDefault(x => x.Name == RoleName) != null);

                DiscordRole? DiscordRole = await ctx.Guild.CreateRoleAsync(RoleName);
                if (DiscordRole == null)
                {
                    await ctx.CreateResponseAsync($"Unable to create role. Check Permissions as this role already exists.", true);
                    return;
                }

                ulong? HostId = null;
                string? HostName = null;
                if (Host == null)
                {
                    HostId = (ulong)0;
                    HostName = "clear";
                }
                else
                {
                    if (Host.IsBot)
                    {
                        HostId = (ulong)0;
                        HostName = "clear";
                    }
                    else
                    {
                        HostId = Host.Id;
                        HostName = Host.Username;
                    }
                }


                try
                {
                    Schedule NewEvent = new((DateTime)StartTime, (DateTime)EndTime, ctx.Guild.Id, EventName, HostURL, (ulong)DiscordRole.Id, HostId: (ulong)HostId, HostName: HostName, WorldLink: WorldLink, EventDescription: Description, ImageURL: Image);
                    await NewEvent.Update();

                    var dbEvent = db.Schedules.FirstOrDefault(x => x.RoleId == (ulong)DiscordRole.Id);
                    if (dbEvent != null)
                    {
                        DiscordMessageBuilder MBuilder = dbEvent.BuildMessage();

                        try
                        {
                            var Message = await ctx.Guild.GetChannel((ulong)ServerSetting.ChannelId).SendMessageAsync(MBuilder);
                            dbEvent.EventId = Message.Id;
                            await dbEvent.Update();
                        }
                        catch
                        {
                            await ctx.CreateResponseAsync($"There was an error making your event.", true);

                        }
                    }
                    await ctx.CreateResponseAsync($"Here you go!", true);

                }
                catch(Exception ex) 
                {
                    await DiscordRole.DeleteAsync();
                    await ctx.CreateResponseAsync($"There was an error making your event.", true);
                }
            }
        }


        [SlashCommand("Edit", "Edit Event.")]
        [SlashRequireUserPermissions(Permissions.ManageMessages)]
        public async Task Edit(
            InteractionContext ctx,
            [Option("EventId", "The ID of the Event", false)] string MessageId,
            [Option("Name", "Name of the event", false)] string EventName = null,
            [Option("Description", "Event Detials", false)] string Description = null,
            [Option("EventStart", "When the event occurs", false)] string EventStart = null,
            [Option("Duration", "How many hours till this event ends?", false)] double EventEnd = 0.0,
            [Option("Host", "User Hosting Event. Tag bot to remove clear role.", false)] DiscordUser Host = null,
            [Option("ProfileURL", "VRC Profile User Hosting Event", false)] string HostURL = null,
            [Option("World", "Link to world. Type 'clear' to remove link", false)] string? WorldLink = null,
            [Option("ImageURL", "Image URL. Type \'clear\' to remove link", false)] string Image = null
            )
        {
            Regex R = new Regex(@"([0-9]*)");

            if (!R.IsMatch(MessageId))
            {
                await ctx.CreateResponseAsync($"Not a valid message Id", true);
                return;
            }

            using (var db = new DBEntities())
            {
                var ServerSetting = db.ServerSettings.FirstOrDefault(x => x.ServerId == ctx.Guild.Id) ?? new ServerSetting(ctx.Guild.Id);
                if (ServerSetting.ChannelId == null)
                {
                    await ctx.CreateResponseAsync($"No Event Channel Set. Have admin set channel using /setEventChannel", true);
                    return;
                }

                Schedule? Schedule = null;

                try
                {
                    ulong EventId = ulong.Parse(R.Match(MessageId).Value);

                    Schedule = db.Schedules.FirstOrDefault(x => x.EventId == EventId);
                    if (Schedule == null)
                    {
                        await ctx.CreateResponseAsync($"Unable to get an event of that Id", true);
                        return;
                    }
                }
                catch
                {
                    await ctx.CreateResponseAsync($"Unable to get an event of that Id", true);
                    return;
                }

                if (!string.IsNullOrEmpty(EventName))
                {
                    Schedule.EventTitle = EventName;
                }

                if (!string.IsNullOrEmpty(Description))
                {
                    Schedule.EventDescription = Description;
                }
                
                if (!string.IsNullOrEmpty(EventStart))
                {
                    try
                    {
                        DateTime? StartTime = null;
                        Regex TimeCode = new Regex(@"\<t:(\d*):[a-zA-Z]{1}\>");
                        if (TimeCode.IsMatch(EventStart))
                        {

                            long unixTimeStamp = long.Parse(TimeCode.Match(EventStart).Groups[1].Value);
                            System.DateTime dtDateTime = new DateTime(1970, 1, 1, 0, 0, 0, 0, System.DateTimeKind.Utc);
                            StartTime = dtDateTime.AddSeconds(unixTimeStamp);
                        }
                        else
                        {
                            StartTime = DateTime.Parse(EventStart);
                        }
                        Schedule.StartTime = StartTime.Value;
                    }
                    catch
                    {
                        await ctx.CreateResponseAsync($"Not a valid Start Time Format", true);
                        return;
                    }
                }

                if (EventEnd > 0)
                {
                    try
                    {
                        DateTime? EndTime = null;
                        EndTime = Schedule.StartTime.AddHours((double)EventEnd);
                        Schedule.EndTime = EndTime.Value;
                    }
                    catch
                    {
                        await ctx.CreateResponseAsync($"Not a valid End Time Format", true);
                        return;
                    }
                }

                try
                {
                    Regex URL = new Regex(@"^http:\/\/|^https:\/\/");
                    if (!string.IsNullOrEmpty(HostURL))
                    {
                        if (!URL.IsMatch(HostURL))
                        {
                            await ctx.CreateResponseAsync(@$"Not a valid Host URL. Ensure link starts with http:// or https://", true);
                            return;
                        }
                        Schedule.HostURL = HostURL;
                    }


                    if (!string.IsNullOrEmpty(WorldLink))
                    {
                        if (WorldLink.Trim().ToLower() == "clear")
                        {
                            Schedule.WorldLink = null;
                        }
                        else
                        {
                            if (!URL.IsMatch(WorldLink))
                            {
                                await ctx.CreateResponseAsync(@$"Not a valid World Link. Ensure link starts with http:// or https://", true);
                                return;
                            }
                            Schedule.WorldLink = WorldLink;
                        }
                    }

                    if (!string.IsNullOrEmpty(Image))
                    {
                        if (Image.Trim().ToLower() == "clear")
                        {
                            Schedule.ImageURL = null;
                        }
                        else
                        {
                            if (!URL.IsMatch(Image))
                            {
                                await ctx.CreateResponseAsync(@$"Not a valid Image Link. Ensure link starts with http:// or https://", true);
                                return;
                            }
                            Schedule.ImageURL = Image;
                        }
                    }
                }
                catch
                {
                    await ctx.CreateResponseAsync(@$"Not a valid Image, Host or World URL. Ensure link starts with http:// or https://", true);
                    return;
                }



                if (Host != null)
                {
                    if (Host.IsBot == true)
                    {
                        Schedule.HostId = (ulong)0;
                        Schedule.HostName = "clear";
                    }
                    else
                    {
                        Schedule.HostId = Host.Id;
                        Schedule.HostName = Host.Username;
                    }
                }

                try
                {
                    DiscordMessageBuilder MBuilder = Schedule.BuildMessage();
                    try
                    {
                        var Message = await ctx.Guild.GetChannel((ulong)ServerSetting.ChannelId).GetMessageAsync(Schedule.EventId);
                        await Message.ModifyAsync(MBuilder);
                        await Schedule.Update();
                        await ctx.CreateResponseAsync($"Here you go!", true);
                    }
                    catch (Exception e)
                    {
                        Console.WriteLine(e);
                        await ctx.CreateResponseAsync($"There was an error updating your event.", true);
                    }
                }
                catch (Exception e)
                {
                    Console.WriteLine(e);
                    await ctx.CreateResponseAsync($"There was an error updating your event.", true);

                }
            }
        }
        
        private static Regex TimeCode = new Regex(@"\<t:(\d*):[a-zA-Z]{1}\>");
        private static Regex VrcUserUrl = new Regex(@"https:\/\/vrchat\.com\/home\/user\/usr_([a-zA-Z0-9-]{36})");
        private static Regex VrcWorldUrl = new Regex(@"https:\/\/vrchat\.com\/home\/world\/wrld_([a-zA-Z0-9-]{36})");

        private static TimeSpan CstOffset = TimeSpan.FromHours(-6);
        
        private async Task CleanupRoles(List<DiscordRole> roles)
        {
            foreach (var discordRole in roles)
            {
                await discordRole.DeleteAsync();
            }
        }

        // [SlashCommand("CleanupAllEventRoles", "Cleanup all event roles, dangerous with existing events!")]
        // [SlashRequireUserPermissions(Permissions.ManageMessages)]
        // public async Task CleanupAllEventRoles(InteractionContext ctx)
        // {
        //     await ctx.DeferAsync(true);
        //     var roleName = String.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISCORD_EVENT_ROLE_PREFIX")) ? "EventRole" : Environment.GetEnvironmentVariable("DISCORD_EVENT_ROLE_PREFIX");
        //
        //     var rolesToCleanUp = ctx.Guild.Roles.Values.Where(role => role.Name.StartsWith(roleName)).ToList();
        //     await CleanupRoles(rolesToCleanUp);
        //
        //     await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent("Done!"));
        // }

        [SlashCommand("ImportEvents", "Import events from TeamUp CSV Export")]
        [SlashRequireUserPermissions(Permissions.ManageMessages)]
        public async Task ImportEvents(
            InteractionContext ctx,
            [Option("TeamUpCsv", "CSV Exported from TeamUp", false)] DiscordAttachment csv)
        {
            await ctx.DeferAsync(true);
            List<DiscordRole> createdRoles = new List<DiscordRole>();
            List<Schedule> createdSchedules = new List<Schedule>();
            await using var db = new DBEntities();
            await using var transaction = await db.Database.BeginTransactionAsync();
            
            var ServerSetting = db.ServerSettings.FirstOrDefault(x => x.ServerId == ctx.Guild.Id) ??
                                new ServerSetting(ctx.Guild.Id);
            if (ServerSetting.ChannelId == null)
            {
                await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent(
                    $"No Event Channel Set. Have admin set channel using /setEventChannel"));
                await transaction.RollbackAsync();
                return;
            }

            // Download CSV from csv.url, parse it as data
            HttpClient client = new HttpClient();
            var stream = await client.GetStreamAsync(csv.Url);
            StreamReader reader = new StreamReader(stream);
            using var csvReader = new CsvReader(reader, CultureInfo.InvariantCulture);
            var records = csvReader.GetRecords<TeamUpEvent>();
            var events = records.ToList();

            foreach (var e in events)
            {
                // TODO: Convert this from hardcoded CST offset to something else?
                var startDate = new DateTimeOffset(DateTime.Parse($"{e.StartDate} {e.StartTime}"), CstOffset);
                var endDate =  new DateTimeOffset(DateTime.Parse($"{e.EndDate} {e.EndTime}"), CstOffset);
                
                // Parse the first match of VrcUserUrl
                var userUrlMatch = VrcUserUrl.Match(e.Who);
                var userUrl = userUrlMatch.Success ? userUrlMatch.Groups[0].Value : "";
                var worldUrlMatch = VrcWorldUrl.Match(e.Location);
                var worldUrl = worldUrlMatch.Success ? worldUrlMatch.Groups[0].Value : null;

                var description = e.Description
                    .Replace("\\[", "[")
                    .Replace("\\]", "]")
                    .Replace("\\*", "*")
                    .Replace("\u00A0", ""); // NBSP
                description = WebUtility.HtmlDecode(description);
                // Find and replace all instances of links in the format of [http://thing.com](https://thing.com), discord doesn't like those for some reason lmao
                Regex regex = new Regex(@"\[(http[s]?:\/\/[^]]+)\]\(\1\)", RegexOptions.Multiline);
                description = regex.Replace(description, "$1 ");
                
                var BaseRoleName = String.IsNullOrEmpty(Environment.GetEnvironmentVariable("DISCORD_EVENT_ROLE_PREFIX")) ? "EventRole" : Environment.GetEnvironmentVariable("DISCORD_EVENT_ROLE_PREFIX");
                string RoleName;
                int i = 0;
                do
                {
                    i++;
                    RoleName = $"{BaseRoleName}-{i}";
                }
                while (ctx.Guild.Roles.Values.FirstOrDefault(x => x.Name == RoleName) != null || createdRoles.FirstOrDefault(x => x.Name == RoleName) != null);

                DiscordRole? DiscordRole = await ctx.Guild.CreateRoleAsync(RoleName);
                if (DiscordRole == null)
                {
                    await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent($"Unable to create role. Check Permissions as this role already exists."));
                    await transaction.RollbackAsync();
                    await CleanupRoles(createdRoles);
                    return;
                }
                createdRoles.Add(DiscordRole);

                try
                {
                    // foreach (var systemTimeZone in TimeZoneInfo.GetSystemTimeZones())
                    // {
                    //     Console.WriteLine(systemTimeZone.DisplayName);
                    // }
                    Schedule NewEvent = new(startDate.UtcDateTime, endDate.UtcDateTime, ctx.Guild.Id, e.Subject, userUrl, (ulong)DiscordRole.Id, HostId: 0, HostName: "clear", WorldLink: worldUrl, EventDescription: description, ImageURL: null);
                    await NewEvent.Update(db);
                    createdSchedules.Add(NewEvent);

                    var dbEvent = db.Schedules.FirstOrDefault(x => x.RoleId == (ulong)DiscordRole.Id);
                    if (dbEvent != null)
                    {
                        try
                        {
                            DiscordMessageBuilder MBuilder = dbEvent.BuildMessage();
                                    
                            var Message = await ctx.Guild.GetChannel((ulong)ServerSetting.ChannelId).SendMessageAsync(MBuilder);
                            dbEvent.EventId = Message.Id;
                            await dbEvent.Update(db);
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine(ex);
                            await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent($"There was an error making your event. Ensure your description is not too long (1024 chars max for the whole embed)."));
                            await transaction.RollbackAsync();
                            await CleanupRoles(createdRoles);
                            return;

                        }
                    }
                }
                catch(Exception ex) 
                {
                    Console.WriteLine(ex);
                    await DiscordRole.DeleteAsync();
                    await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent($"There was an error making your events."));
                    await transaction.RollbackAsync();
                    await CleanupRoles(createdRoles);
                    return;
                }
            }

            // Create txt file attachment with summary
            var summary = await ComposeEventSummary(ctx, createdSchedules);
            var filePath = $"{ctx.InteractionId}.txt";
            await File.WriteAllTextAsync(filePath, summary);
            using var fs = new FileStream(filePath, FileMode.Open, FileAccess.Read);
            
            await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent($"Here you go!").AddFile(fs));
            
            // Cleanup file
            if (File.Exists(filePath))
            {
                File.Delete(filePath);
            }
            
            await transaction.CommitAsync();
        }

        private async Task<string> ComposeEventSummary(InteractionContext ctx, List<Schedule> schedules)
        {
            using var db = new DBEntities();
            
            string output = "";
            var serverSetting = db.ServerSettings.FirstOrDefault(x => x.ServerId == ctx.Guild.Id) ??
                                new ServerSetting(ctx.Guild.Id);
            var channel = ctx.Guild.GetChannel((ulong)serverSetting.ChannelId);
            
            schedules.Sort((a, b) => a.StartTime.CompareTo(b.StartTime));
            for (var i = 0; i < schedules.Count; i++)
            {
                var schedule = schedules[i];
                var number = i + 1;

                var utcTime = new DateTimeOffset(schedule.StartTime);
                var localTime = utcTime.ToOffset(CstOffset);
                var dayOfTheWeek = localTime.ToString("dddd");
                
                var discordTimeString = $"<t:{utcTime.ToUnixTimeSeconds()}:F>";

                var message = await channel.GetMessageAsync(schedule.EventId);
                var messageUrl = message.JumpLink;

                output +=
                    $"📅  {number}.  {dayOfTheWeek}: [**{schedule.EventTitle}**]({messageUrl}) on {discordTimeString}\n";
                          // $"{schedule.EventDescription}\n";

                // List<string> links = new List<string>();
                
                // if (!string.IsNullOrEmpty(schedule.HostURL))
                // {
                //     links.Add($"[Add The Host]({schedule.HostURL})");
                // }
                // links.Add($"[Sign up here!]({messageUrl})");
                // if (!string.IsNullOrEmpty(schedule.WorldLink))
                // {
                //     links.Add($"[World Location]({schedule.WorldLink})\n");
                // }
                // links.Add($"[VRChat Group](https://vrc.group/NOFACE.0408)");
                // links.Add($"[Discord](https://discord.gg/thefaceless)");
                //
                // output += $"{string.Join(" - ", links)}\n";
                //
                // output += "\n";
            }

            return output;
        }
    }
}
