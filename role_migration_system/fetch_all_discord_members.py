import os
import asyncio
import pandas as pd
import discord
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
OUTPUT_DIR = 'outputs'

async def fetch_all_guild_members():
    """
    Fetch all members from The Faceless Discord server with their full details.
    """
    # Set up intents - we need members intent
    intents = discord.Intents.default()
    intents.guilds = True
    intents.members = True  # Required to fetch all members
    
    # Create bot instance
    bot = commands.Bot(command_prefix='!', intents=intents)
    
    all_members = []
    
    @bot.event
    async def on_ready():
        print(f'Bot connected as {bot.user}')
        
        # Target The Faceless server
        FACELESS_GUILD_ID = 480695542155051010
        guild = bot.get_guild(FACELESS_GUILD_ID)
        
        if not guild:
            print(f"ERROR: Could not find The Faceless guild (ID: {FACELESS_GUILD_ID})")
            await bot.close()
            return
        
        print(f"\nFetching members from: {guild.name} (ID: {guild.id})")
        print(f"Total members: {guild.member_count}")
        
        # Fetch all members - this might take a while for large servers
        print("Fetching all members... (this may take a moment)")
        
        # Use chunk_guilds to ensure we have all members
        await bot.chunk_guild(guild)
        
        members_processed = 0
        
        for member in guild.members:
            member_data = {
                'user_id': member.id,
                'username': member.name,  # Discord username
                'display_name': member.display_name,  # Server nickname or username
                'nick': member.nick,  # Server nickname (None if not set)
                'discriminator': member.discriminator,  # The 4-digit tag (legacy)
                'global_name': member.global_name if hasattr(member, 'global_name') else None,  # New global display name
                'bot': member.bot,
                'joined_at': member.joined_at.isoformat() if member.joined_at else None,
                'created_at': member.created_at.isoformat(),
                'roles': [role.name for role in member.roles if role.name != '@everyone'],
                'role_ids': [str(role.id) for role in member.roles if role.name != '@everyone'],
                'top_role': member.top_role.name if member.top_role.name != '@everyone' else None,
                'status': str(member.status) if hasattr(member, 'status') else 'unknown',
                'premium_since': member.premium_since.isoformat() if member.premium_since else None,
            }
            
            all_members.append(member_data)
            members_processed += 1
            
            # Progress update
            if members_processed % 100 == 0:
                print(f"  Processed {members_processed}/{guild.member_count} members...")
        
        print(f"\nSuccessfully fetched {len(all_members)} members")
        
        # Convert to DataFrame
        df = pd.DataFrame(all_members)
        
        # Save full member list
        output_path = os.path.join(OUTPUT_DIR, 'faceless_all_members.csv')
        df.to_csv(output_path, index=False)
        print(f"Saved full member list to: {output_path}")
        
        # Also save a simplified version for username mapping
        simple_df = df[['user_id', 'username', 'display_name', 'nick', 'global_name', 'bot']].copy()
        simple_output_path = os.path.join(OUTPUT_DIR, 'faceless_members_simple.csv')
        simple_df.to_csv(simple_output_path, index=False)
        print(f"Saved simplified member list to: {simple_output_path}")
        
        # Create a username lookup table (all possible names a user might be known by)
        lookup_data = []
        for _, member in df.iterrows():
            user_id = member['user_id']
            
            # Add all possible name variations
            names_to_add = set()
            
            if pd.notna(member['username']):
                names_to_add.add(member['username'])
            if pd.notna(member['display_name']):
                names_to_add.add(member['display_name'])
            if pd.notna(member['nick']):
                names_to_add.add(member['nick'])
            if pd.notna(member['global_name']):
                names_to_add.add(member['global_name'])
            
            for name in names_to_add:
                lookup_data.append({
                    'lookup_name': name.lower(),  # Store lowercase for case-insensitive matching
                    'original_name': name,
                    'user_id': user_id,
                    'username': member['username'],
                    'is_bot': member['bot']
                })
        
        lookup_df = pd.DataFrame(lookup_data)
        lookup_output_path = os.path.join(OUTPUT_DIR, 'faceless_username_lookup.csv')
        lookup_df.to_csv(lookup_output_path, index=False)
        print(f"Saved username lookup table to: {lookup_output_path}")
        
        # Print summary statistics
        print(f"\nSummary:")
        print(f"  Total members: {len(df)}")
        print(f"  Human members: {len(df[~df['bot']])}")
        print(f"  Bot members: {len(df[df['bot']])}")
        print(f"  Members with nicknames: {len(df[df['nick'].notna()])}")
        print(f"  Unique usernames in lookup: {len(lookup_df['lookup_name'].unique())}")
        
        await bot.close()
    
    try:
        await bot.start(DISCORD_BOT_TOKEN)
    except Exception as e:
        print(f"Error: {e}")
        await bot.close()

if __name__ == "__main__":
    asyncio.run(fetch_all_guild_members())