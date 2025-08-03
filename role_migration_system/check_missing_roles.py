import pandas as pd

# Load all roles
all_roles = pd.read_csv('outputs/all_discord_roles.csv', dtype={'role_id': str})
faceless_roles = all_roles[all_roles['guild_id'] == 480695542155051010]

print(f"Total Faceless roles: {len(faceless_roles)}")

# Check for missing roles
missing_roles = ['Meditation', 'Portal Posse', 'Wotagei', 'Pole Dancing', 'VR Fundamentals', 'CHILL']

print("\nSearching for missing roles:")
for role_name in missing_roles:
    matches = faceless_roles[faceless_roles['role_name'].str.contains(role_name, case=False, na=False)]
    print(f"\n{role_name}: {len(matches)} matches")
    if len(matches) > 0:
        for _, match in matches.iterrows():
            print(f"  ID: {match['role_id']}, Name: {match['role_name']}")

# Also check production roles current
print("\n\nChecking production_roles_current file:")
prod_roles = pd.read_csv('outputs/production_roles_current_20250802_224649.csv', dtype={'role_id': str})
for role_name in missing_roles:
    matches = prod_roles[prod_roles['role_name'].str.contains(role_name, case=False, na=False)]
    if len(matches) > 0:
        print(f"\n{role_name} in current production:")
        for _, match in matches.iterrows():
            print(f"  ID: {match['role_id']}, Name: {match['role_name']}")