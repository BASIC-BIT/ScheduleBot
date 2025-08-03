import discord
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

print("Starting bare minimum test...")

async def main():
    print("Creating client...")
    client = discord.Client(intents=discord.Intents.default())
    
    @client.event
    async def on_ready():
        print(f'Success! Bot is {client.user}')
        await client.close()
    
    print("Starting bot...")
    try:
        await client.start(os.getenv('DISCORD_BOT_TOKEN'))
    except Exception as e:
        print(f"Error: {e}")

print("Running asyncio...")
asyncio.run(main())
print("Done!")