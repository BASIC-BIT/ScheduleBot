import discord
import asyncio
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

async def verify_roles_exist():
    """Verify that all roles in our assignments exist on the server"""
    
    # Load assignments
    assignments = pd.read_csv('outputs/user_role_assignments_AUTHORITATIVE_20250802_225050.csv',
                             dtype={'role_id': str, 'user_id': str})
    
    # Get unique roles
    unique_roles = assignments[['role_id', 'role_name']].drop_duplicates()
    print(f"Checking {len(unique_roles)} unique roles...")
    
    intents = discord.Intents.default()
    intents.guilds = True
    
    bot = discord.Client(intents=intents)
    
    @bot.event
    async def on_ready():
        guild = bot.get_guild(480695542155051010)  # The Faceless
        
        if not guild:
            print("ERROR: Could not find guild!")
            await bot.close()
            return
        
        print(f"Connected to: {guild.name}")
        print("-" * 50)
        
        found = 0
        not_found = 0
        
        for _, role_data in unique_roles.iterrows():
            role_id = int(role_data['role_id'])
            role_name = role_data['role_name']
            
            role = guild.get_role(role_id)
            
            if role:
                found += 1
                print(f"✓ {role_name} ({role_id}) - FOUND")
            else:
                not_found += 1
                print(f"✗ {role_name} ({role_id}) - NOT FOUND")
        
        print("-" * 50)
        print(f"Summary: {found} found, {not_found} not found")
        
        await bot.close()
    
    await bot.start(os.getenv('DISCORD_BOT_TOKEN'))

if __name__ == "__main__":
    asyncio.run(verify_roles_exist())