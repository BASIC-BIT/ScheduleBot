import discord
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def check_test_server_roles():
    intents = discord.Intents.default()
    intents.guilds = True
    
    bot = discord.Client(intents=intents)
    
    @bot.event
    async def on_ready():
        test_guild = bot.get_guild(1249723747896918109)
        prod_guild = bot.get_guild(480695542155051010)
        
        if test_guild:
            print("Test Server Roles (BASIC's Creations):")
            print("="*50)
            for role in sorted(test_guild.roles, key=lambda r: r.position, reverse=True)[:30]:
                if not role.is_default():
                    print(f"  {role.name:30} (ID: {role.id})")
        
        if prod_guild:
            print("\n\nProduction Server Class Roles (The Faceless):")
            print("="*50)
            # Load our class roles
            import pandas as pd
            class_roles_df = pd.read_csv('outputs/relevant_class_roles.csv')
            for _, role_data in class_roles_df.head(10).iterrows():
                print(f"  {role_data['role_name']:30} (ID: {int(role_data['role_id'])})")
        
        await bot.close()
    
    await bot.start(os.getenv('DISCORD_BOT_TOKEN'))

if __name__ == "__main__":
    asyncio.run(check_test_server_roles())