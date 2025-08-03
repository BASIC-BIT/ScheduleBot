import discord
import asyncio
import os
import time
from dotenv import load_dotenv

load_dotenv()

async def debug_timeout():
    print(f"Start time: {time.time()}")
    
    intents = discord.Intents.default()
    intents.guilds = True
    intents.members = True
    
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f'Bot connected at {time.time()}')
        
        guild = client.get_guild(480695542155051010)
        
        if guild:
            print(f"Guild found: {guild.name}")
            print(f"Initial members: {len(guild.members)}")
            
            # Check if we need to enable chunking
            if not guild.chunked:
                print("Guild not chunked, requesting chunks...")
                await guild.chunk()
                print(f"After chunking: {len(guild.members)} members")
        
        await client.close()
    
    print("Starting bot...")
    await client.start(os.getenv('DISCORD_BOT_TOKEN'))
    print(f"End time: {time.time()}")

asyncio.run(debug_timeout())