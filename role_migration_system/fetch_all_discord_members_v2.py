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
    intents.presences = False  # Don't need presence updates
    
    print("Setting up bot with member intents...")
    print("NOTE: This requires the 'Server Members Intent' to be enabled in the Discord Developer Portal!")
    
    # Create bot instance
    bot = commands.Bot(command_prefix='!', intents=intents)
    
    all_members = []
    
    @bot.event
    async def on_ready():
        print(f'Bot connected as {bot.user}')
        print(f'Bot is in {len(bot.guilds)} guilds')
        
        # Target The Faceless server
        FACELESS_GUILD_ID = 480695542155051010
        guild = bot.get_guild(FACELESS_GUILD_ID)
        
        if not guild:
            print(f"ERROR: Could not find The Faceless guild (ID: {FACELESS_GUILD_ID})")
            print("Available guilds:")
            for g in bot.guilds:
                print(f"  - {g.name} (ID: {g.id})")
            await bot.close()
            return
        
        print(f"\nFetching members from: {guild.name} (ID: {guild.id})")
        print(f"Guild member count: {guild.member_count}")
        print(f"Members cached: {len(guild.members)}")
        
        # Check if we need to fetch members
        if len(guild.members) < guild.member_count:
            print(f"\nNeed to fetch members (only {len(guild.members)} of {guild.member_count} cached)")
            print("Fetching all members... (this may take a moment)")
            
            try:
                # Try multiple methods to ensure we get all members
                print("Method 1: Using fetch_members()...")
                member_count = 0
                async for member in guild.fetch_members(limit=None):
                    member_data = {
                        'user_id': member.id,
                        'username': member.name,  # Discord username
                        'display_name': member.display_name,  # Server nickname or username
                        'nick': member.nick,  # Server nickname (None if not set)
                        'discriminator': member.discriminator,  # The 4-digit tag (legacy)
                        'global_name': getattr(member, 'global_name', None),  # New global display name
                        'bot': member.bot,
                        'joined_at': member.joined_at.isoformat() if member.joined_at else None,
                        'created_at': member.created_at.isoformat(),
                        'roles': [role.name for role in member.roles if role.name != '@everyone'],
                        'role_ids': [str(role.id) for role in member.roles if role.name != '@everyone'],
                        'top_role': member.top_role.name if member.top_role.name != '@everyone' else None,
                        'premium_since': member.premium_since.isoformat() if member.premium_since else None,
                    }
                    
                    all_members.append(member_data)
                    member_count += 1
                    
                    # Progress update
                    if member_count % 100 == 0:
                        print(f"  Fetched {member_count} members...")
                
                print(f"Method 1 complete: Fetched {member_count} members")
                
            except Exception as e:
                print(f"Error with fetch_members: {e}")
                print("Trying alternative method...")
                
                # Alternative: Try chunk_guild
                try:
                    print("Method 2: Using chunk_guild()...")
                    await guild.chunk()
                    
                    for member in guild.members:
                        member_data = {
                            'user_id': member.id,
                            'username': member.name,
                            'display_name': member.display_name,
                            'nick': member.nick,
                            'discriminator': member.discriminator,
                            'global_name': getattr(member, 'global_name', None),
                            'bot': member.bot,
                            'joined_at': member.joined_at.isoformat() if member.joined_at else None,
                            'created_at': member.created_at.isoformat(),
                            'roles': [role.name for role in member.roles if role.name != '@everyone'],
                            'role_ids': [str(role.id) for role in member.roles if role.name != '@everyone'],
                            'top_role': member.top_role.name if member.top_role.name != '@everyone' else None,
                            'premium_since': member.premium_since.isoformat() if member.premium_since else None,
                        }
                        all_members.append(member_data)
                    
                    print(f"Method 2 complete: Got {len(all_members)} members")
                except Exception as e2:
                    print(f"Error with chunk_guild: {e2}")
        else:
            # Members already cached
            print("All members already cached, processing...")
            for member in guild.members:
                member_data = {
                    'user_id': member.id,
                    'username': member.name,
                    'display_name': member.display_name,
                    'nick': member.nick,
                    'discriminator': member.discriminator,
                    'global_name': getattr(member, 'global_name', None),
                    'bot': member.bot,
                    'joined_at': member.joined_at.isoformat() if member.joined_at else None,
                    'created_at': member.created_at.isoformat(),
                    'roles': [role.name for role in member.roles if role.name != '@everyone'],
                    'role_ids': [str(role.id) for role in member.roles if role.name != '@everyone'],
                    'top_role': member.top_role.name if member.top_role.name != '@everyone' else None,
                    'premium_since': member.premium_since.isoformat() if member.premium_since else None,
                }
                all_members.append(member_data)
        
        print(f"\nSuccessfully processed {len(all_members)} members")
        print("Converting to DataFrame...")
        
        if len(all_members) == 0:
            print("\nERROR: No members fetched!")
            print("Possible causes:")
            print("1. The bot doesn't have the 'Server Members Intent' enabled")
            print("2. The bot doesn't have permission to view members")
            print("\nTo fix:")
            print("1. Go to https://discord.com/developers/applications")
            print("2. Select your bot application")
            print("3. Go to 'Bot' section")
            print("4. Enable 'Server Members Intent' under Privileged Gateway Intents")
            await bot.close()
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(all_members)
        print(f"DataFrame created with {len(df)} rows")
        
        # Save full member list
        output_path = os.path.join(OUTPUT_DIR, 'faceless_all_members.csv')
        print(f"Saving full member list to: {output_path}...")
        df.to_csv(output_path, index=False)
        print(f"✓ Saved full member list")
        
        # Also save a simplified version for username mapping
        print("Creating simplified member list...")
        simple_df = df[['user_id', 'username', 'display_name', 'nick', 'global_name', 'bot']].copy()
        simple_output_path = os.path.join(OUTPUT_DIR, 'faceless_members_simple.csv')
        print(f"Saving simplified list to: {simple_output_path}...")
        simple_df.to_csv(simple_output_path, index=False)
        print(f"✓ Saved simplified member list")
        
        # Create a username lookup table (all possible names a user might be known by)
        print("Creating username lookup table...")
        lookup_data = []
        total_members = len(df)
        for idx, (_, member) in enumerate(df.iterrows()):
            if idx % 100 == 0:
                print(f"  Processing lookup data: {idx}/{total_members} members...")
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
        
        print(f"Creating lookup DataFrame with {len(lookup_data)} entries...")
        lookup_df = pd.DataFrame(lookup_data)
        lookup_output_path = os.path.join(OUTPUT_DIR, 'faceless_username_lookup.csv')
        print(f"Saving lookup table to: {lookup_output_path}...")
        lookup_df.to_csv(lookup_output_path, index=False)
        print(f"✓ Saved username lookup table")
        
        # Print summary statistics
        print(f"\nSummary:")
        print(f"  Total members: {len(df)}")
        print(f"  Human members: {len(df[~df['bot']])}")
        print(f"  Bot members: {len(df[df['bot']])}")
        print(f"  Members with nicknames: {len(df[df['nick'].notna()])}")
        print(f"  Unique usernames in lookup: {len(lookup_df['lookup_name'].unique())}")
        
        print("\nAll files saved successfully!")
        await bot.close()
    
    try:
        await bot.start(DISCORD_BOT_TOKEN)
    except Exception as e:
        print(f"Error starting bot: {e}")
        await bot.close()

if __name__ == "__main__":
    asyncio.run(fetch_all_guild_members())