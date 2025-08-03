import os
import asyncio
import pandas as pd
import discord
from discord.ext import commands
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
OUTPUT_DIR = 'outputs'

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def fetch_members_simple():
    """Simple member fetch with minimal processing."""
    
    intents = discord.Intents.default()
    intents.members = True
    intents.guilds = True
    
    bot = commands.Bot(command_prefix='!', intents=intents)
    
    @bot.event
    async def on_ready():
        print(f'Bot connected as {bot.user}')
        
        FACELESS_GUILD_ID = 480695542155051010
        guild = bot.get_guild(FACELESS_GUILD_ID)
        
        if not guild:
            print("ERROR: Guild not found!")
            await bot.close()
            return
        
        print(f"Guild: {guild.name}")
        print(f"Members: {len(guild.members)}/{guild.member_count}")
        
        # Simple list to store just the essential data
        members_data = []
        
        print("\nProcessing members...")
        for i, member in enumerate(guild.members):
            if i % 100 == 0:
                print(f"  {i}/{len(guild.members)} members processed...")
            
            # Just store the basics
            members_data.append({
                'user_id': str(member.id),  # Convert to string to avoid issues
                'username': member.name,
                'display_name': member.display_name,
                'nick': member.nick if member.nick else "",
                'bot': member.bot
            })
        
        print(f"\nProcessed {len(members_data)} members")
        
        # Save as CSV
        try:
            print("Saving to CSV...")
            import csv
            
            output_path = os.path.join(OUTPUT_DIR, 'faceless_members_basic.csv')
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                if members_data:
                    writer = csv.DictWriter(f, fieldnames=members_data[0].keys())
                    writer.writeheader()
                    writer.writerows(members_data)
            
            print(f"✓ Saved to {output_path}")
            
            # Also create lookup file
            print("\nCreating lookup file...")
            lookup_data = []
            
            for member in members_data:
                # Add username
                if member['username']:
                    lookup_data.append({
                        'lookup_name': member['username'].lower(),
                        'original_name': member['username'],
                        'user_id': member['user_id']
                    })
                
                # Add display name if different
                if member['display_name'] and member['display_name'] != member['username']:
                    lookup_data.append({
                        'lookup_name': member['display_name'].lower(),
                        'original_name': member['display_name'],
                        'user_id': member['user_id']
                    })
                
                # Add nick if exists
                if member['nick']:
                    lookup_data.append({
                        'lookup_name': member['nick'].lower(),
                        'original_name': member['nick'],
                        'user_id': member['user_id']
                    })
            
            lookup_path = os.path.join(OUTPUT_DIR, 'faceless_username_lookup.csv')
            
            with open(lookup_path, 'w', newline='', encoding='utf-8') as f:
                if lookup_data:
                    writer = csv.DictWriter(f, fieldnames=lookup_data[0].keys())
                    writer.writeheader()
                    writer.writerows(lookup_data)
            
            print(f"✓ Saved lookup to {lookup_path}")
            print(f"  Total lookup entries: {len(lookup_data)}")
            
        except Exception as e:
            print(f"ERROR saving files: {e}")
            import traceback
            traceback.print_exc()
        
        await bot.close()
        print("\nDone!")
    
    try:
        await bot.start(DISCORD_BOT_TOKEN)
    except Exception as e:
        print(f"Bot error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(fetch_members_simple())