import discord
import asyncio
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = 'outputs'

async def rebuild_with_current_roles():
    """Rebuild assignments using current role IDs from Discord"""
    
    print("REBUILDING ASSIGNMENTS WITH CURRENT DISCORD ROLE IDs")
    print("="*80)
    
    # Load our assignments from the AUTHORITATIVE file
    assignments = pd.read_csv(os.path.join(OUTPUT_DIR, 'user_role_assignments_AUTHORITATIVE_20250802_225050.csv'),
                             dtype={'role_id': str, 'user_id': str})
    
    print(f"Loaded {len(assignments)} assignments")
    
    # Remove Community Manager
    cm_mask = assignments['role_name'] == 'Community Manager'
    assignments = assignments[~cm_mask]
    print(f"Removed {cm_mask.sum()} Community Manager assignments")
    
    intents = discord.Intents.default()
    intents.guilds = True
    
    bot = discord.Client(intents=intents)
    
    @bot.event
    async def on_ready():
        print("\nFetching current roles from Discord...")
        
        guild = bot.get_guild(480695542155051010)  # The Faceless
        
        if not guild:
            print("ERROR: Could not find guild!")
            await bot.close()
            return
        
        # Build role name to ID mapping from Discord
        role_name_to_id = {}
        
        # Keywords to identify class/event roles
        keywords = [
            'dj', 'dance', 'yoga', 'vocal', 'meditation', 'coding', 'blender', 'unity',
            'photography', 'asl', 'breakin', 'waltz', 'bachata', 'vibe', 'beyond',
            'gogo', 'go-go', 'pole', 'podcast', 'portal', 'posse', 'vr fundamental',
            'music production', 'sociology', 'esoteric', 'chill', 'loft', 'wotagei',
            'house', 'animation', 'art class'
        ]
        
        print("\nCurrent Discord roles:")
        print("-"*50)
        
        for role in guild.roles:
            if role.is_default():
                continue
                
            role_name_lower = role.name.lower()
            
            # Check if this is a class/event role
            for keyword in keywords:
                if keyword in role_name_lower:
                    role_name_to_id[role.name] = str(role.id)
                    print(f"  {role.name:30} -> {role.id}")
                    break
        
        print(f"\nFound {len(role_name_to_id)} class/event roles on Discord")
        
        # Now fix our assignments
        print("\nFixing role IDs in assignments...")
        
        fixed_count = 0
        missing_roles = set()
        role_fixes = {}
        
        for idx, row in assignments.iterrows():
            role_name = row['role_name']
            old_role_id = row['role_id']
            
            # Try exact match first
            new_role_id = None
            if role_name in role_name_to_id:
                new_role_id = role_name_to_id[role_name]
            else:
                # Try case-insensitive match
                for discord_name, discord_id in role_name_to_id.items():
                    if role_name.lower() == discord_name.lower():
                        new_role_id = discord_id
                        break
                
                # Try partial match for special cases
                if not new_role_id:
                    if role_name == "GOGO Dance" or role_name == "Go-Go Dance":
                        for discord_name, discord_id in role_name_to_id.items():
                            if "gogo" in discord_name.lower() or "go-go" in discord_name.lower():
                                new_role_id = discord_id
                                break
            
            if new_role_id and new_role_id != old_role_id:
                assignments.at[idx, 'role_id'] = new_role_id
                fixed_count += 1
                
                if role_name not in role_fixes:
                    role_fixes[role_name] = {'old': old_role_id, 'new': new_role_id}
            elif not new_role_id:
                missing_roles.add(role_name)
        
        print(f"\nFixed {fixed_count} role IDs")
        
        if role_fixes:
            print("\nRole ID updates:")
            for role_name, fix in sorted(role_fixes.items()):
                print(f"  {role_name}: {fix['old']} -> {fix['new']}")
        
        if missing_roles:
            print(f"\nWARNING: {len(missing_roles)} roles not found on Discord:")
            for role in sorted(missing_roles):
                print(f"  - {role}")
            
            # Remove assignments for missing roles
            before_count = len(assignments)
            assignments = assignments[~assignments['role_name'].isin(missing_roles)]
            removed_count = before_count - len(assignments)
            print(f"\nRemoved {removed_count} assignments for missing roles")
        
        # Remove duplicates by consolidating
        print("\nConsolidating duplicate user-role pairs...")
        assignments = assignments.groupby(['user_id', 'role_id', 'username', 'role_name'], as_index=False).agg({
            'schedule_bot_events': 'sum',
            'discord_scheduled_events': 'sum',
            'manual_interest_events': 'sum'
        })
        
        # Save the final file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(OUTPUT_DIR, f'user_role_assignments_DISCORD_VERIFIED_{timestamp}.csv')
        
        # Ensure dtypes are preserved
        assignments['role_id'] = assignments['role_id'].astype(str)
        assignments['user_id'] = assignments['user_id'].astype(str)
        
        assignments.to_csv(output_path, index=False)
        
        print(f"\n[SUCCESS] Saved Discord-verified assignments to: {output_path}")
        
        # Final statistics
        print("\nFinal Statistics:")
        print("-"*50)
        print(f"Total assignments: {len(assignments)}")
        print(f"Unique users: {len(assignments['user_id'].unique())}")
        print(f"Unique roles: {len(assignments['role_id'].unique())}")
        
        # Verify all role IDs are valid
        print("\nVerifying all role IDs...")
        all_valid = True
        for role_id in assignments['role_id'].unique():
            role = guild.get_role(int(role_id))
            if not role:
                print(f"  ERROR: Role ID {role_id} not found!")
                all_valid = False
        
        if all_valid:
            print("  ✓ All role IDs verified!")
        
        await bot.close()
    
    await bot.start(os.getenv('DISCORD_BOT_TOKEN'))

if __name__ == "__main__":
    asyncio.run(rebuild_with_current_roles())