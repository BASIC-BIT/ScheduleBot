{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft": "Warning",
      "Microsoft.Hosting.Lifetime": "Information"
    }
  },
  "AllowedHosts": "*",
  "ConnectionStrings": {
    "DefaultConnection": "Server=${mysql_host};Database=${mysql_database};User=${mysql_user};Password=${mysql_password};"
  },
  "DiscordBot": {
    "Token": "${discord_token}",
    "CommandPrefix": "!"
  },
  "Environment": "${environment}",
  "Storage": {
    "Type": "LocalFileSystem",
    "LocalPath": "/opt/schedulebot/data/images",
    "S3Bucket": ${s3_bucket == null ? "null" : "\"${s3_bucket}\""}
  }
} 