import discord
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def debug_bot_roles():
    """Debug bot roles and permissions more thoroughly"""
    
    intents = discord.Intents.default()
    intents.guilds = True
    intents.members = True
    
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f'Bot User: {client.user} (ID: {client.user.id})')
        
        guild = client.get_guild(480695542155051010)  # The Faceless
        
        if not guild:
            print("ERROR: Could not find guild!")
            await client.close()
            return
        
        # Find the bot member
        bot_member = guild.get_member(client.user.id)
        if not bot_member:
            print("ERROR: Bot not found as member!")
            await client.close()
            return
        
        print(f"\nBot Member: {bot_member} (ID: {bot_member.id})")
        print("="*80)
        
        # List ALL roles the bot has
        print("\nALL Bot Roles (including @everyone):")
        for role in bot_member.roles:
            print(f"  - {role.name} (ID: {role.id}, position: {role.position})")
            if not role.is_default():
                # Check this specific role's permissions
                print(f"    Permissions value: {role.permissions.value}")
                print(f"    Has manage_roles: {role.permissions.manage_roles}")
        
        # Check for role named "MeetingNotesBot" or similar
        print("\nSearching for bot-related roles in guild:")
        for role in guild.roles:
            if any(name in role.name.lower() for name in ['meeting', 'notes', 'bot', 'schedule']):
                in_bot = "✓ BOT HAS THIS" if role in bot_member.roles else "✗ Bot doesn't have this"
                print(f"  {role.name} (ID: {role.id}) - {in_bot}")
                if role.permissions.manage_roles:
                    print(f"    ^ This role has manage_roles permission!")
        
        # Check guild-level permissions
        print(f"\nGuild-level permissions for bot:")
        print(f"  Permission integer: {bot_member.guild_permissions.value}")
        
        # Try a different way to check permissions
        print("\nChecking permissions another way:")
        channel = guild.text_channels[0] if guild.text_channels else None
        if channel:
            channel_perms = channel.permissions_for(bot_member)
            print(f"  In #{channel.name}:")
            print(f"    manage_roles: {channel_perms.manage_roles}")
            print(f"    send_messages: {channel_perms.send_messages}")
        
        # Test if we can actually use the role assignment API
        print("\nTesting role assignment capability:")
        test_role_id = 1392209391872250027  # House Dance
        test_role = guild.get_role(test_role_id)
        if test_role:
            print(f"  Test role: {test_role.name}")
            print(f"  Bot can theoretically assign: {bot_member.top_role.position > test_role.position}")
        
        await client.close()
    
    await client.start(os.getenv('DISCORD_BOT_TOKEN'))

if __name__ == "__main__":
    asyncio.run(debug_bot_roles())