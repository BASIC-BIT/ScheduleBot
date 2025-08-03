import discord
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    intents = discord.Intents.default()
    intents.guilds = True
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f'Bot connected as {client.user}')
        
        # Test both servers
        test_guild = client.get_guild(1249723747896918109)  # Test server
        prod_guild = client.get_guild(480695542155051010)   # Production
        
        print(f"\nTest guild: {test_guild.name if test_guild else 'NOT FOUND'}")
        print(f"Prod guild: {prod_guild.name if prod_guild else 'NOT FOUND'}")
        
        if prod_guild:
            print(f"Prod guild members loaded: {len(prod_guild.members)}")
            
            # Test a specific role
            asl_role = prod_guild.get_role(1392210986387116173)
            print(f"ASL Class role: {asl_role.name if asl_role else 'NOT FOUND'}")
        
        await client.close()
    
    await client.start(os.getenv('DISCORD_BOT_TOKEN'))

asyncio.run(main())