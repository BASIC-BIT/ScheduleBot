variable "discord_bot_token" {
  description = "The token of your discord bot."
  type = string
}

variable "mysql_password" {
  description = "MySQL password"
  type        = string
  sensitive   = true
}

variable GITHUB_TOKEN {
  sensitive = true
}
variable AWS_TOKEN_KEY {
  sensitive = true
}
variable DISCORD_CLIENT_ID {
  sensitive = true
}