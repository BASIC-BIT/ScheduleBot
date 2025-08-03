import discord
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    intents = discord.Intents.default()
    intents.guilds = True
    intents.members = True  # Need this to see all members
    
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f'Bot connected as {client.user}')
        
        guild = client.get_guild(480695542155051010)
        
        if guild:
            print(f"\nGuild: {guild.name}")
            print(f"Members cached: {len(guild.members)}")
            
            # Try fetching members
            print("\nFetching all members...")
            async for member in guild.fetch_members(limit=None):
                pass  # Just iterate to load them
            
            print(f"After fetch: {len(guild.members)} members")
            
            # Test finding a specific user
            test_user_id = 211750261922725888  # basic_bit
            member = guild.get_member(test_user_id)
            print(f"\nTest user basic_bit: {member.name if member else 'NOT FOUND'}")
        
        await client.close()
    
    await client.start(os.getenv('DISCORD_BOT_TOKEN'))

asyncio.run(main())