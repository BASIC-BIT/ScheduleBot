import discord
import asyncio
import os
import csv
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

async def fetch_current_production_roles():
    """Fetch current roles from production server"""
    
    intents = discord.Intents.default()
    intents.guilds = True
    
    bot = discord.Client(intents=intents)
    
    @bot.event
    async def on_ready():
        print("Bot connected, fetching production server roles...")
        
        guild = bot.get_guild(480695542155051010)  # The Faceless
        
        if not guild:
            print("ERROR: Could not find production guild!")
            await bot.close()
            return
        
        print(f"Connected to: {guild.name}")
        print(f"Total roles: {len(guild.roles)}")
        
        # Keywords to identify class/event roles
        keywords = [
            'dj', 'dance', 'yoga', 'vocal', 'meditation', 'coding', 'blender', 'unity',
            'photography', 'asl', 'breakin', 'waltz', 'bachata', 'vibe', 'beyond',
            'gogo', 'go-go', 'pole', 'podcast', 'portal', 'posse', 'vr fundamental',
            'music production', 'sociology', 'esoteric', 'chill', 'loft', 'wotagei',
            'house', 'animation', 'art class', 'community manager'
        ]
        
        # Find relevant roles
        relevant_roles = []
        for role in guild.roles:
            if role.is_default():
                continue
            
            role_name_lower = role.name.lower()
            for keyword in keywords:
                if keyword in role_name_lower:
                    relevant_roles.append({
                        'role_id': str(role.id),
                        'role_name': role.name,
                        'member_count': len(role.members),
                        'created_at': role.created_at.isoformat()
                    })
                    break
        
        print(f"\nFound {len(relevant_roles)} relevant roles")
        
        # Save to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f'outputs/production_roles_current_{timestamp}.csv'
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['role_id', 'role_name', 'member_count', 'created_at'])
            writer.writeheader()
            writer.writerows(relevant_roles)
        
        print(f"\nSaved current roles to: {output_path}")
        
        # Show comparison with our data
        print("\nComparing with our assignments data...")
        import pandas as pd
        
        # Load our role IDs
        assignments = pd.read_csv('outputs/user_role_assignments_PRODUCTION_READY_20250802_224433.csv')
        our_role_ids = set(assignments['role_id'].astype(str).unique())
        
        # Current role IDs
        current_role_ids = {r['role_id'] for r in relevant_roles}
        current_role_names = {r['role_name'].lower() for r in relevant_roles}
        
        # Find mismatches
        missing_from_server = our_role_ids - current_role_ids
        print(f"\nRole IDs in our data but NOT on server: {len(missing_from_server)}")
        
        if missing_from_server:
            # Try to match by name
            our_roles = assignments[['role_id', 'role_name']].drop_duplicates()
            print("\nAttempting to match by role name:")
            for _, row in our_roles.iterrows():
                if str(row['role_id']) in missing_from_server:
                    role_name_lower = row['role_name'].lower()
                    # Find similar role on server
                    matches = [r for r in relevant_roles if r['role_name'].lower() == role_name_lower]
                    if matches:
                        print(f"  {row['role_name']}: Our ID {row['role_id']} -> Server ID {matches[0]['role_id']}")
                    else:
                        # Try partial match
                        partial_matches = [r for r in relevant_roles if role_name_lower in r['role_name'].lower() or r['role_name'].lower() in role_name_lower]
                        if partial_matches:
                            print(f"  {row['role_name']}: Our ID {row['role_id']} -> Maybe {partial_matches[0]['role_name']} ({partial_matches[0]['role_id']})?")
                        else:
                            print(f"  {row['role_name']}: Our ID {row['role_id']} -> NO MATCH FOUND")
        
        await bot.close()
    
    await bot.start(os.getenv('DISCORD_BOT_TOKEN'))

if __name__ == "__main__":
    asyncio.run(fetch_current_production_roles())