# VRChat UDON Integration API

This document provides information about the VRChat UDON Integration API, which allows VRChat worlds to access schedule data from the Scheduling Assistant.

## API Endpoints

### Get Events

```
GET /api/events
```

Retrieves a list of events with pagination and filtering options.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | integer | 1 | The page number to retrieve |
| pageSize | integer | 10 | The number of items per page (max: 50) |
| serverId | ulong | null | Filter by Discord server ID |
| startDate | datetime | null | Filter events starting after this date (ISO 8601 format) |
| endDate | datetime | null | Filter events ending before this date (ISO 8601 format) |
| isActive | boolean | null | Filter by active status |
| hasEnded | boolean | null | Filter by ended status |

#### Response Format

```json
{
  "pagination": {
    "currentPage": 1,
    "pageSize": 10,
    "totalItems": 45,
    "totalPages": 5
  },
  "events": [
    {
      "id": 123,
      "eventTitle": "VRChat Meetup",
      "eventDescription": "Let's meet in VRChat!",
      "startTime": "2023-07-15T18:00:00Z",
      "endTime": "2023-07-15T20:00:00Z",
      "hostName": "EventHost",
      "worldLink": "https://vrchat.com/home/world/wrld_abc123",
      "imageUrl": "https://your-s3-bucket.s3.amazonaws.com/events/123.jpg",
      "isActive": true,
      "hasEnded": false
    },
    // More events...
  ]
}
```

## UDON Integration

To integrate this API with your VRChat world using UDON, you can use UdonSharp to make HTTP requests to the API endpoint.

### Example UdonSharp Code

```csharp
using UdonSharp;
using UnityEngine;
using VRC.SDK3.StringLoading;
using VRC.SDKBase;
using VRC.Udon;

public class EventFetcher : UdonSharpBehaviour
{
    public string apiUrl = "https://your-api-url.com/api/events";
    public int pageSize = 10;
    public GameObject eventPrefab;
    public Transform eventContainer;
    
    private VRCStringDownloader _stringDownloader;
    
    void Start()
    {
        _stringDownloader = new VRCStringDownloader();
        FetchEvents();
    }
    
    public void FetchEvents()
    {
        string url = $"{apiUrl}?pageSize={pageSize}";
        _stringDownloader.DownloadString(url, (IUdonEventReceiver)this);
    }
    
    public override void OnStringLoadSuccess(string downloadedString)
    {
        Debug.Log("Events loaded successfully");
        // Parse the JSON and create event objects
        // Note: You'll need to use a JSON parser compatible with UDON
        // Display the events in your world
    }
    
    public override void OnStringLoadError(string error)
    {
        Debug.LogError($"Error loading events: {error}");
    }
}
```

## Authentication

Currently, the API is open and does not require authentication. In the future, API key authentication will be implemented for security.

## Image Hosting

Event images are hosted in an AWS S3 bucket with public read access. The `imageUrl` field in the API response contains the full URL to the image.

## Error Handling

The API returns standard HTTP status codes:

- 200: Success
- 400: Bad Request (invalid parameters)
- 500: Internal Server Error

Error responses include a JSON object with an error message:

```json
{
  "error": "An error occurred while retrieving events."
}
```

## Rate Limiting

There are currently no rate limits in place, but please be considerate with your API usage to ensure availability for all users.

## Support

For issues or questions about the API, please contact the Scheduling Assistant team. 