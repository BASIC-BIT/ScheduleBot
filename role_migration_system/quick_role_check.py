import discord
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def quick_role_check():
    """Quick check of specific roles"""
    
    intents = discord.Intents.default()
    intents.guilds = True
    
    bot = discord.Client(intents=intents)
    
    @bot.event
    async def on_ready():
        print("Connected to Discord")
        
        guild = bot.get_guild(480695542155051010)  # The Faceless
        
        if not guild:
            print("ERROR: Could not find guild!")
            await bot.close()
            return
        
        print(f"Guild: {guild.name}")
        print("-"*50)
        
        # Test specific role IDs from our data
        test_roles = [
            ('1392210986387116173', 'ASL Class'),
            ('1392210566407524382', 'YOGA'),
            ('1163047310889062420', 'DJ'),
            ('1392211365455724605', 'Meditation'),
        ]
        
        print("Testing role IDs from our data:")
        for role_id_str, expected_name in test_roles:
            role_id = int(role_id_str)
            role = guild.get_role(role_id)
            if role:
                print(f"  ✓ {role_id} -> {role.name} (expected: {expected_name})")
            else:
                print(f"  ✗ {role_id} -> NOT FOUND (expected: {expected_name})")
        
        print("\nSearching for these roles by name:")
        for role in guild.roles:
            if any(name in role.name for name in ['ASL', 'YOGA', 'DJ', 'Meditation']):
                print(f"  {role.name}: {role.id}")
        
        await bot.close()
    
    try:
        await bot.start(os.getenv('DISCORD_BOT_TOKEN'))
    except:
        print("Bot connection failed")

if __name__ == "__main__":
    asyncio.run(quick_role_check())