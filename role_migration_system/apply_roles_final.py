import os
import asyncio
import pandas as pd
import discord
from discord.ext import commands
import aiohttp
from ratelimit import limits, sleep_and_retry
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
OUTPUT_DIR = 'outputs'

# Rate limiting: Discord allows 50 requests per second for bots
@sleep_and_retry
@limits(calls=45, period=1)  # Stay under limit with buffer
async def add_role_to_user(guild_id, user_id, role_id, session, headers):
    """Rate-limited function to add a role to a user"""
    url = f"https://discord.com/api/v10/guilds/{guild_id}/members/{user_id}/roles/{role_id}"
    async with session.put(url, headers=headers) as response:
        return response.status, user_id, role_id

async def apply_roles_to_users(assignments_file, target_guild_id, dry_run=True, test_limit=None):
    """
    Apply roles to users based on the reviewed assignments.
    
    Args:
        assignments_file: Path to CSV file with user role assignments
        target_guild_id: The guild ID to apply roles to
        dry_run: If True, only simulate the actions without applying
        test_limit: If set, only process this many assignments (for testing)
    """
    # Load assignments
    print(f"Loading assignments from: {assignments_file}")
    # CRITICAL: Read with proper dtype to preserve large integers
    assignments_df = pd.read_csv(assignments_file, dtype={'role_id': str, 'user_id': str})
    
    if test_limit:
        print(f"TEST MODE: Limiting to {test_limit} assignments")
        assignments_df = assignments_df.head(test_limit)
    
    # DEBUG: Show first few assignments
    print("\nFirst 5 assignments:")
    print(assignments_df[['user_id', 'username', 'role_id', 'role_name']].head())
    
    intents = discord.Intents.default()
    intents.guilds = True
    intents.members = True
    
    bot = commands.Bot(command_prefix='!', intents=intents)
    
    @bot.event
    async def on_ready():
        print(f'Bot connected as {bot.user}')
        print(f'DEBUG: on_ready called')
        
        # Get the target guild
        print(f'DEBUG: Getting guild {target_guild_id}')
        guild = bot.get_guild(target_guild_id)
        if not guild:
            print(f"ERROR: Could not find guild with ID {target_guild_id}")
            await bot.close()
            return
        
        print(f"\nTarget Guild: {guild.name} (ID: {guild.id})")
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE - APPLYING ROLES'}")
        print("=" * 80)
        print(f'DEBUG: About to group assignments')
        
        # Group assignments by role for efficiency
        role_groups = assignments_df.groupby(['role_id', 'role_name'])
        
        total_assignments = len(assignments_df)
        successful = 0
        failed = 0
        already_has_role = 0
        user_not_found = 0
        role_not_found = 0
        
        # Prepare for API calls
        headers = {
            'Authorization': f'Bot {DISCORD_BOT_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        if not dry_run and not test_limit:
            # Final confirmation for production run
            print(f"\nABOUT TO APPLY {total_assignments} ROLE ASSIGNMENTS!")
            print("This action cannot be easily undone.")
            confirmation = input("Type 'YES' to proceed, anything else to cancel: ")
            
            if confirmation != 'YES':
                print("Operation cancelled.")
                await bot.close()
                return
        
        print("\nProcessing role assignments...")
        
        # Track progress
        assignments_processed = 0
        
        async with aiohttp.ClientSession() as session:
            for (role_id, role_name), group in role_groups:
                # Keep role_id as string, convert to int only for Discord API
                try:
                    role_id_int = int(role_id)  # Convert string to int for Discord API
                except:
                    print(f"\nERROR: Invalid role ID: {role_id}")
                    failed += len(group)
                    continue
                    
                role = guild.get_role(role_id_int)
                
                if not role:
                    print(f"\nWARNING: Role '{role_name}' (ID: {role_id}) not found in guild!")
                    role_not_found += len(group)
                    failed += len(group)
                    continue
                
                print(f"\nProcessing role: {role_name} ({len(group)} users)")
                
                for _, assignment in group.iterrows():
                    try:
                        user_id = int(assignment['user_id'])  # Convert string to int
                    except:
                        print(f"  ✗ Invalid user ID: {assignment['user_id']}")
                        failed += 1
                        assignments_processed += 1
                        continue
                    
                    username = assignment['username']
                    
                    try:
                        # Check if member exists in guild
                        member = guild.get_member(user_id)
                        
                        if not member:
                            # Skip fetch_member to avoid API calls
                            if assignments_processed < 20:  # Only show first 20 to avoid spam
                                print(f"  ✗ User {username} ({user_id}) not found in guild cache")
                            user_not_found += 1
                            assignments_processed += 1
                            continue
                        
                        # Check if member already has the role
                        if role in member.roles:
                            if assignments_processed < 20:
                                print(f"  ⚠ {member.name} already has role {role_name}")
                            already_has_role += 1
                            assignments_processed += 1
                            continue
                        
                        if dry_run:
                            if assignments_processed < 50:  # Show first 50 in dry run
                                print(f"  [DRY RUN] Would add {role_name} to {member.name} ({member.id})")
                            successful += 1
                        else:
                            # Apply the role
                            status, _, _ = await add_role_to_user(guild.id, user_id, role_id_int, session, headers)
                            
                            if status == 204:  # Success
                                if assignments_processed < 20:
                                    print(f"  ✓ Added {role_name} to {member.name} ({member.id})")
                                successful += 1
                            else:
                                print(f"  ✗ Failed to add {role_name} to {member.name} - Status: {status}")
                                failed += 1
                    
                    except Exception as e:
                        print(f"  ✗ Error processing user {username} ({user_id}): {str(e)}")
                        failed += 1
                    
                    assignments_processed += 1
                    
                    # Progress update
                    if assignments_processed % 50 == 0:
                        print(f"\n  Progress: {assignments_processed}/{total_assignments} processed...")
        
        # Final summary
        print("\n" + "=" * 80)
        print("FINAL SUMMARY:")
        print(f"Total assignments processed: {total_assignments}")
        print(f"Successful: {successful}")
        print(f"Already had role: {already_has_role}")
        print(f"User not found: {user_not_found}")
        print(f"Role not found: {role_not_found}")
        print(f"Failed: {failed}")
        
        # Save summary report
        summary = {
            'timestamp': datetime.now().isoformat(),
            'guild_id': target_guild_id,
            'guild_name': guild.name,
            'dry_run': dry_run,
            'test_limit': test_limit,
            'total_assignments': total_assignments,
            'successful': successful,
            'already_has_role': already_has_role,
            'user_not_found': user_not_found,
            'role_not_found': role_not_found,
            'failed': failed
        }
        
        summary_path = os.path.join(OUTPUT_DIR, f'role_application_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nSummary saved to: {summary_path}")
        
        await bot.close()
    
    print(f'DEBUG: About to start bot')
    try:
        await bot.start(DISCORD_BOT_TOKEN)
    except Exception as e:
        print(f"Error: {e}")
        await bot.close()


if __name__ == "__main__":
    import sys
    
    # Configuration
    PRODUCTION_SERVER_ID = 480695542155051010  # The Faceless
    TEST_SERVER_ID = 1249723747896918109  # BASIC's Creations
    
    # Use the final fixed file with DJ Class and missing roles removed
    assignments_file = 'outputs/user_role_assignments_FINAL_FIXED_20250802_232315.csv'
    
    if not os.path.exists(assignments_file):
        print(f"ERROR: Assignments file not found: {assignments_file}")
        sys.exit(1)
    
    print(f"Using assignments file: {assignments_file}")
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            print("Running TEST server dry run with limit of 10...")
            asyncio.run(apply_roles_to_users(assignments_file, TEST_SERVER_ID, dry_run=True, test_limit=10))
        elif sys.argv[1] == 'test-apply':
            print("Running TEST server LIVE APPLICATION with limit of 10...")
            asyncio.run(apply_roles_to_users(assignments_file, TEST_SERVER_ID, dry_run=False, test_limit=10))
        elif sys.argv[1] == 'production-dry':
            print("Running PRODUCTION server DRY RUN...")
            asyncio.run(apply_roles_to_users(assignments_file, PRODUCTION_SERVER_ID, dry_run=True))
        elif sys.argv[1] == 'production-apply':
            print("Running PRODUCTION server LIVE APPLICATION...")
            print("WARNING: This will apply roles to ALL users in the production server!")
            asyncio.run(apply_roles_to_users(assignments_file, PRODUCTION_SERVER_ID, dry_run=False))
        else:
            print("Unknown command:", sys.argv[1])
    else:
        print("Usage:")
        print("  python apply_roles_final.py test              # Test server dry run (10 users)")
        print("  python apply_roles_final.py test-apply        # Test server apply (10 users)")
        print("  python apply_roles_final.py production-dry    # Production server dry run")
        print("  python apply_roles_final.py production-apply  # Production server APPLY ROLES")