import os
import asyncio
import pandas as pd
import discord
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
OUTPUT_DIR = 'outputs'

async def apply_roles_optimized(assignments_file, target_guild_id, dry_run=True, test_limit=None):
    """Optimized version with better debugging and efficiency"""
    
    # Load assignments
    print(f"Loading assignments from: {assignments_file}")
    assignments_df = pd.read_csv(assignments_file, dtype={'role_id': str, 'user_id': str})
    
    if test_limit:
        print(f"TEST MODE: Limiting to {test_limit} assignments")
        assignments_df = assignments_df.head(test_limit)
    
    print(f"Total assignments to process: {len(assignments_df)}")
    
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
        print(f"Members cached: {len(guild.members)}")
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE - APPLYING ROLES'}")
        print("=" * 80)
        
        # Pre-fetch all guild roles to verify they exist
        guild_roles = {str(role.id): role for role in guild.roles}
        print(f"Guild has {len(guild_roles)} roles")
        
        # Pre-fetch all members to avoid individual API calls
        print("\nCaching all guild members...")
        members_dict = {member.id: member for member in guild.members}
        print(f"Cached {len(members_dict)} members")
        
        # Process assignments
        results = {
            'successful': 0,
            'already_has_role': 0,
            'user_not_found': 0,
            'role_not_found': 0,
            'failed': 0
        }
        
        # Group by role for efficiency
        role_groups = assignments_df.groupby(['role_id', 'role_name'])
        
        for (role_id_str, role_name), group in role_groups:
            print(f"\nProcessing role: {role_name} (ID: {role_id_str})")
            
            # Check if role exists
            if role_id_str not in guild_roles:
                print(f"  ✗ Role not found in guild!")
                results['role_not_found'] += len(group)
                continue
            
            role = guild_roles[role_id_str]
            print(f"  ✓ Found role: {role.name} ({len(group)} assignments)")
            
            # Process users for this role
            for idx, (_, assignment) in enumerate(group.iterrows()):
                if idx < 5 or (idx % 50 == 0):  # Show first 5 and progress updates
                    print(f"    Processing {idx+1}/{len(group)}...")
                
                try:
                    user_id = int(assignment['user_id'])
                    username = assignment['username']
                    
                    # Check if member exists (already cached)
                    if user_id not in members_dict:
                        if idx < 10:  # Only show first 10
                            print(f"      ✗ {username} ({user_id}) - not in guild")
                        results['user_not_found'] += 1
                        continue
                    
                    member = members_dict[user_id]
                    
                    # Check if member already has role
                    if role in member.roles:
                        if idx < 10:
                            print(f"      ⚠ {member.name} - already has role")
                        results['already_has_role'] += 1
                        continue
                    
                    # Would add role (or actually add it if not dry run)
                    if dry_run:
                        if idx < 10:
                            print(f"      ✓ {member.name} - would add role")
                        results['successful'] += 1
                    else:
                        try:
                            await member.add_roles(role, reason="Role migration from ScheduleBot")
                            if idx < 10:
                                print(f"      ✓ {member.name} - role added")
                            results['successful'] += 1
                        except Exception as e:
                            print(f"      ✗ {member.name} - failed: {e}")
                            results['failed'] += 1
                
                except Exception as e:
                    print(f"      ✗ Error processing assignment: {e}")
                    results['failed'] += 1
        
        # Summary
        print("\n" + "="*80)
        print("SUMMARY:")
        print(f"Total assignments: {len(assignments_df)}")
        for key, value in results.items():
            print(f"{key}: {value}")
        
        # Save summary
        summary = {
            'timestamp': datetime.now().isoformat(),
            'guild_id': target_guild_id,
            'guild_name': guild.name,
            'dry_run': dry_run,
            'test_limit': test_limit,
            'total_assignments': len(assignments_df),
            **results
        }
        
        import json
        summary_path = os.path.join(OUTPUT_DIR, f'role_application_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nSummary saved to: {summary_path}")
        
        await bot.close()
    
    await bot.start(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    import sys
    
    # Configuration
    PRODUCTION_SERVER_ID = 480695542155051010  # The Faceless
    TEST_SERVER_ID = 1249723747896918109  # BASIC's Creations
    
    assignments_file = 'outputs/user_role_assignments_AUTHORITATIVE_20250802_225050.csv'
    
    if not os.path.exists(assignments_file):
        print(f"ERROR: Assignments file not found: {assignments_file}")
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            print("Running TEST server dry run with limit of 10...")
            asyncio.run(apply_roles_optimized(assignments_file, TEST_SERVER_ID, dry_run=True, test_limit=10))
        elif sys.argv[1] == 'production-dry':
            print("Running PRODUCTION server DRY RUN...")
            asyncio.run(apply_roles_optimized(assignments_file, PRODUCTION_SERVER_ID, dry_run=True))
        elif sys.argv[1] == 'production-apply':
            print("Running PRODUCTION server LIVE APPLICATION...")
            print("WARNING: This will apply roles to ALL users!")
            confirmation = input("Type 'YES' to proceed: ")
            if confirmation == 'YES':
                asyncio.run(apply_roles_optimized(assignments_file, PRODUCTION_SERVER_ID, dry_run=False))
            else:
                print("Cancelled.")
        else:
            print("Unknown command:", sys.argv[1])
    else:
        print("Usage:")
        print("  python apply_roles_optimized.py test              # Test server dry run")
        print("  python apply_roles_optimized.py production-dry    # Production server dry run")
        print("  python apply_roles_optimized.py production-apply  # Production server APPLY ROLES")