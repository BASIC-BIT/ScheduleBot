import os
import asyncio
import pandas as pd
import discord
from discord.ext import commands
import json
from datetime import datetime
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
OUTPUT_DIR = 'outputs'

# Rate limiting settings
RATE_LIMIT_DELAY = 1.0  # Delay between each role assignment (in seconds)
BATCH_SIZE = 10  # Number of assignments before a longer pause
BATCH_DELAY = 5.0  # Longer delay after each batch

async def apply_roles_to_users(assignments_file, target_guild_id, dry_run=True, test_limit=None):
    """
    Apply roles to users with proper rate limiting.
    
    Args:
        assignments_file: Path to CSV file with user role assignments
        target_guild_id: The guild ID to apply roles to
        dry_run: If True, only simulate the actions without applying
        test_limit: If set, only process this many assignments (for testing)
    """
    # Load assignments
    print(f"Loading assignments from: {assignments_file}")
    assignments_df = pd.read_csv(assignments_file, dtype={'role_id': str, 'user_id': str})
    
    if test_limit:
        print(f"TEST MODE: Limiting to {test_limit} assignments")
        assignments_df = assignments_df.head(test_limit)
    
    print(f"\nTotal assignments to process: {len(assignments_df)}")
    
    intents = discord.Intents.default()
    intents.guilds = True
    intents.members = True
    
    bot = commands.Bot(command_prefix='!', intents=intents)
    
    @bot.event
    async def on_ready():
        print(f'Bot connected as {bot.user}')
        
        # Get the target guild
        guild = bot.get_guild(target_guild_id)
        if not guild:
            print(f"ERROR: Could not find guild with ID {target_guild_id}")
            await bot.close()
            return
        
        print(f"\nTarget Guild: {guild.name} (ID: {guild.id})")
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE - APPLYING ROLES'}")
        print("=" * 80)
        
        # Group assignments by role for efficiency
        role_groups = assignments_df.groupby(['role_id', 'role_name'])
        
        total_assignments = len(assignments_df)
        successful = 0
        failed = 0
        already_has_role = 0
        user_not_found = 0
        role_not_found = 0
        
        if not dry_run and not test_limit:
            # Final confirmation for production run
            print(f"\nABOUT TO APPLY {total_assignments} ROLE ASSIGNMENTS!")
            print("This action cannot be easily undone.")
            print(f"Rate limiting: {RATE_LIMIT_DELAY}s between assignments, {BATCH_DELAY}s every {BATCH_SIZE} assignments")
            confirmation = input("Type 'YES' to proceed, anything else to cancel: ")
            
            if confirmation != 'YES':
                print("Operation cancelled.")
                await bot.close()
                return
        
        print("\nProcessing role assignments...")
        
        # Track progress
        assignments_processed = 0
        start_time = time.time()
        
        for (role_id, role_name), group in role_groups:
            try:
                role_id_int = int(role_id)
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
            
            for idx, (_, assignment) in enumerate(group.iterrows()):
                try:
                    user_id = int(assignment['user_id'])
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
                        if assignments_processed < 20:
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
                        if assignments_processed < 50:
                            print(f"  [DRY RUN] Would add {role_name} to {member.name} ({member.id})")
                        successful += 1
                    else:
                        # Apply the role with proper rate limiting
                        try:
                            await member.add_roles(role, reason="ScheduleBot role migration")
                            
                            if assignments_processed < 20 or assignments_processed % 50 == 0:
                                elapsed = time.time() - start_time
                                rate = assignments_processed / elapsed if elapsed > 0 else 0
                                print(f"  ✓ Added {role_name} to {member.name} ({assignments_processed}/{total_assignments} - {rate:.1f}/s)")
                            
                            successful += 1
                            
                            # Rate limiting
                            await asyncio.sleep(RATE_LIMIT_DELAY)
                            
                            # Extra delay after batches
                            if assignments_processed > 0 and assignments_processed % BATCH_SIZE == 0:
                                print(f"\n  [Rate limit pause - {BATCH_DELAY}s]")
                                await asyncio.sleep(BATCH_DELAY)
                                
                        except discord.Forbidden:
                            print(f"  ✗ Permission denied to add {role_name} to {member.name}")
                            failed += 1
                        except discord.HTTPException as e:
                            if e.status == 429:
                                print(f"  ✗ Rate limited! Waiting {e.retry_after}s...")
                                await asyncio.sleep(e.retry_after)
                                # Retry once
                                try:
                                    await member.add_roles(role, reason="ScheduleBot role migration")
                                    successful += 1
                                except:
                                    print(f"  ✗ Failed to add {role_name} to {member.name} after retry")
                                    failed += 1
                            else:
                                print(f"  ✗ Failed to add {role_name} to {member.name}: {e}")
                                failed += 1
                
                except Exception as e:
                    print(f"  ✗ Error processing user {username} ({user_id}): {str(e)}")
                    failed += 1
                
                assignments_processed += 1
                
                # Progress update
                if assignments_processed % 50 == 0:
                    elapsed = time.time() - start_time
                    remaining = total_assignments - assignments_processed
                    eta = remaining * (elapsed / assignments_processed) if assignments_processed > 0 else 0
                    print(f"\n  Progress: {assignments_processed}/{total_assignments} processed ({elapsed:.1f}s elapsed, ~{eta:.1f}s remaining)")
        
        # Final summary
        elapsed_total = time.time() - start_time
        print("\n" + "="*80)
        print("FINAL SUMMARY:")
        print(f"Total time: {elapsed_total:.1f} seconds")
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
            'failed': failed,
            'elapsed_seconds': elapsed_total
        }
        
        summary_path = os.path.join(OUTPUT_DIR, f'role_application_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nSummary saved to: {summary_path}")
        
        await bot.close()
    
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
    
    # Use the final fixed file
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
        print("  python apply_roles_with_proper_rate_limit.py test              # Test server dry run (10 users)")
        print("  python apply_roles_with_proper_rate_limit.py test-apply        # Test server apply (10 users)")
        print("  python apply_roles_with_proper_rate_limit.py production-dry    # Production server dry run")
        print("  python apply_roles_with_proper_rate_limit.py production-apply  # Production server APPLY ROLES")