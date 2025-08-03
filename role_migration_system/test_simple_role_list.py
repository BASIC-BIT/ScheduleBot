import discord
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Simple test without pandas or complex logic
intents = discord.Intents.default()
intents.guilds = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bot connected as {client.user}')
    
    # The Faceless guild
    guild = client.get_guild(480695542155051010)
    
    if guild:
        print(f"\nGuild: {guild.name}")
        print(f"Total roles: {len(guild.roles)}")
        
        # Find ASL Class specifically
        print("\nSearching for ASL Class...")
        for role in guild.roles:
            if 'ASL' in role.name:
                print(f"  Found: {role.name} (ID: {role.id})")
        
        # Test our specific ID
        test_id = 1392210986387116173
        test_role = guild.get_role(test_id)
        print(f"\nTesting role ID {test_id}:")
        if test_role:
            print(f"  Found: {test_role.name}")
        else:
            print(f"  Not found")
    else:
        print("Could not find guild!")
    
    await client.close()

# Run directly
asyncio.run(client.start(os.getenv('DISCORD_BOT_TOKEN')))