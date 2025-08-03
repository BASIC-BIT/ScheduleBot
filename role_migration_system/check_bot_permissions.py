import discord
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def check_bot_permissions():
    """Check bot permissions and role hierarchy"""
    
    intents = discord.Intents.default()
    intents.guilds = True
    intents.members = True
    
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f'Bot connected as {client.user}')
        
        guild = client.get_guild(480695542155051010)  # The Faceless
        
        if not guild:
            print("ERROR: Could not find guild!")
            await client.close()
            return
        
        print(f"\nGuild: {guild.name}")
        print("="*80)
        
        # Find the bot member
        bot_member = guild.get_member(client.user.id)
        if not bot_member:
            print("ERROR: Bot not found as member!")
            await client.close()
            return
        
        # Check bot's roles
        print("\nBot's roles:")
        bot_highest_role = bot_member.top_role
        for role in sorted(bot_member.roles, key=lambda r: r.position, reverse=True):
            if not role.is_default():
                print(f"  {role.name} (position: {role.position})")
        
        print(f"\nBot's highest role: {bot_highest_role.name} (position: {bot_highest_role.position})")
        
        # Check permissions
        print("\nBot's permissions in this guild:")
        perms = bot_member.guild_permissions
        important_perms = [
            'manage_roles', 'administrator', 'manage_guild', 
            'view_channel', 'send_messages', 'read_message_history'
        ]
        
        for perm in important_perms:
            value = getattr(perms, perm, False)
            status = "✓" if value else "✗"
            print(f"  {status} {perm}: {value}")
        
        # Check specific roles we're trying to assign
        print("\nChecking roles we want to assign:")
        print("-"*80)
        
        test_roles = [
            ('House Dance', '1392209391872250027'),
            ('Animation Dance', '1392209677282185446'),
            ('Waltz', '1392210075950649415'),
            ('DJ Class', '1392210777888526366'),
            ('YOGA', '1392210566407524382'),
            ('ASL Class', '1392210986387116173')
        ]
        
        for role_name, role_id in test_roles:
            role = guild.get_role(int(role_id))
            if role:
                can_assign = bot_highest_role.position > role.position
                status = "✓ CAN assign" if can_assign else "✗ CANNOT assign"
                print(f"  {role_name} (position: {role.position}) - {status}")
                
                # Check if role is managed (by integration/bot)
                if role.managed:
                    print(f"    WARNING: This role is managed by an integration!")
                
                # Check role permissions
                if role.permissions.administrator:
                    print(f"    WARNING: This role has administrator permission!")
            else:
                print(f"  {role_name} - NOT FOUND")
        
        # List all roles by position
        print("\nAll roles in guild (by position):")
        print("-"*80)
        
        for role in sorted(guild.roles, key=lambda r: r.position, reverse=True)[:30]:  # Top 30 roles
            marker = " <- BOT" if role in bot_member.roles else ""
            managed = " [MANAGED]" if role.managed else ""
            print(f"  {role.position:3}: {role.name}{marker}{managed}")
        
        await client.close()
    
    await client.start(os.getenv('DISCORD_BOT_TOKEN'))

if __name__ == "__main__":
    asyncio.run(check_bot_permissions())