import discord
import asyncio
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

async def test_minimal():
    # Load just a few rows
    df = pd.read_csv('outputs/user_role_assignments_AUTHORITATIVE_20250802_225050.csv',
                     dtype={'role_id': str, 'user_id': str}, nrows=5)
    
    print(f"Loaded {len(df)} test rows")
    print(df[['username', 'role_name', 'role_id']])
    
    intents = discord.Intents.default()
    intents.guilds = True
    intents.members = True
    
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f'\nBot connected')
        
        guild = client.get_guild(480695542155051010)
        
        if guild:
            print(f"Guild: {guild.name}")
            
            # Test just the first assignment
            row = df.iloc[0]
            role_id = int(row['role_id'])
            user_id = int(row['user_id'])
            
            print(f"\nTesting: {row['username']} -> {row['role_name']}")
            
            role = guild.get_role(role_id)
            print(f"Role exists: {role is not None}")
            
            member = guild.get_member(user_id)
            print(f"Member exists: {member is not None}")
            
            if role and member:
                has_role = role in member.roles
                print(f"Already has role: {has_role}")
        
        await client.close()
    
    await client.start(os.getenv('DISCORD_BOT_TOKEN'))

asyncio.run(test_minimal())