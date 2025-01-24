using CsvHelper.Configuration.Attributes;

namespace SchedulingAssistant.Models;

public class TeamUpEvent
{
    public string Subject { get; set; }
    [Name("Start Date")]
    public string StartDate { get; set; }
    [Name("Start Time")]
    public string StartTime { get; set; }
    [Name("End Date")]
    public string EndDate { get; set; }
    [Name("End Time")]
    public string EndTime { get; set; }
    [Name("All day")]
    public string AllDay { get; set; }
    [Name("Calendar Name")]
    public string CalendarName { get; set; }
    public string Repeats { get; set; }
    [Name("Repeats Until")]
    public string RepeatsUntil { get; set; }
    [Name("Created By")]
    public string CreatedBy { get; set; }
    [Name("Updated By")]
    public string UpdatedBy { get; set; }
    [Name("Creation Date")]
    public string CreationDate { get; set; }
    [Name("Last Update Date")]
    public string LastUpdateDate { get; set; }
    public string Who { get; set; }
    public string Location { get; set; }
    public string Description { get; set; }
    public string Attachments { get; set; }
}