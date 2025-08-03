import pandas as pd
import os

# Load all Discord roles
all_roles_df = pd.read_csv(os.path.join('outputs', 'all_discord_roles.csv'))

# Filter for The Faceless server
PRODUCTION_SERVER_ID = 480695542155051010
production_roles = all_roles_df[all_roles_df['guild_id'] == PRODUCTION_SERVER_ID]

# Expanded keywords list
dance_keywords = [
    'class', 'dance', 'breakin', 'poppin', 'lockin', 'house', 
    'hip hop', 'yoga', 'vocal', 'dj', 'freestyle', 'gogo',
    'robot', 'animation', 'vogue', 'waack', 'choreo', 'movement',
    'art', 'asl', 'podcast', 'photography', 'scare', 'sociology', 
    'music', 'loft', 'vibe', 'bachata', 'waltz', 'esoteric', 
    'blender', 'unity', 'coding', 'dancer', 'meditation', 'pole',
    'wotagei', 'chill', 'portal posse', 'vr fundamentals', 'shufflin',
    'krump', 'tuttin', 'boppin', 'waving', 'liquid', 'particle',
    'improv', 'flow arts', 'beyond dance', 'philosophy', 'languages'
]

# Filter for relevant roles (case insensitive)
pattern = '|'.join(dance_keywords)
relevant_roles = production_roles[
    production_roles['role_name'].str.lower().str.contains(pattern, na=False) &
    ~production_roles['is_bot_role'] &
    ~production_roles['is_default']
].sort_values('role_name')

print(f"Found {len(relevant_roles)} relevant roles")
print("\nRoles found:")
for _, role in relevant_roles.iterrows():
    print(f"  - {role['role_name']} ({role['role_id']})")

# Save to CSV
relevant_roles.to_csv(os.path.join('outputs', 'relevant_class_roles.csv'), index=False)
print(f"\nSaved {len(relevant_roles)} roles to outputs/relevant_class_roles.csv")