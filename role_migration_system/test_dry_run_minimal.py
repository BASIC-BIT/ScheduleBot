import discord
import asyncio
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

async def test_dry_run():
    # Load assignments
    df = pd.read_csv('outputs/user_role_assignments_AUTHORITATIVE_20250802_225050.csv',
                     dtype={'role_id': str, 'user_id': str})
    
    print(f"Loaded {len(df)} assignments")
    print("\nFirst 3 assignments:")
    print(df[['username', 'role_name', 'role_id']].head(3))
    
    # Test just ASL Class
    asl_df = df[df['role_name'] == 'ASL Class']
    print(f"\nASL Class assignments: {len(asl_df)}")
    print(f"ASL Class role ID(s): {asl_df['role_id'].unique()}")
    
    intents = discord.Intents.default()
    intents.guilds = True
    intents.members = True
    
    bot = discord.Client(intents=intents)
    
    @bot.event
    async def on_ready():
        print(f'\nBot connected as {bot.user}')
        
        guild = bot.get_guild(480695542155051010)  # The Faceless
        
        if not guild:
            print("ERROR: Could not find guild!")
            await bot.close()
            return
        
        print(f"Guild: {guild.name}")
        
        # Test ASL Class role
        asl_role_id = int(asl_df['role_id'].iloc[0])
        print(f"\nTesting ASL Class role ID: {asl_role_id}")
        
        role = guild.get_role(asl_role_id)
        if role:
            print(f"✓ Found role: {role.name}")
            
            # Test a few users
            print("\nTesting first 3 ASL assignments:")
            for _, assignment in asl_df.head(3).iterrows():
                user_id = int(assignment['user_id'])
                member = guild.get_member(user_id)
                
                if member:
                    if role in member.roles:
                        print(f"  {member.name} - already has role")
                    else:
                        print(f"  {member.name} - would add role")
                else:
                    print(f"  User {assignment['username']} ({user_id}) - not found")
        else:
            print(f"✗ Role not found!")
        
        await bot.close()
    
    await bot.start(os.getenv('DISCORD_BOT_TOKEN'))

if __name__ == "__main__":
    asyncio.run(test_dry_run())