import os
import pandas as pd
from datetime import datetime

OUTPUT_DIR = 'outputs'

def update_discord_event_subscriber_usernames():
    """
    Update the user_role_assignments_FINAL.csv to replace generic 
    'Discord Event Subscriber' usernames with actual usernames from 
    faceless_members_basic.csv
    """
    print("Loading data files...")
    
    # Load the current assignments
    assignments_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'user_role_assignments_FINAL.csv'))
    print(f"  Loaded {len(assignments_df)} assignments")
    
    # Load the member data with actual usernames
    members_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'faceless_members_basic.csv'))
    print(f"  Loaded {len(members_df)} Discord members")
    
    # Create a lookup dictionary for user_id -> username
    user_lookup = {}
    for _, member in members_df.iterrows():
        user_id = str(member['user_id'])
        username = member['username']
        display_name = member['display_name']
        
        # Prefer display name if it's different from username
        if pd.notna(display_name) and display_name != username:
            user_lookup[user_id] = display_name
        else:
            user_lookup[user_id] = username
    
    print(f"\nCreated lookup for {len(user_lookup)} users")
    
    # Count updates
    updates_made = 0
    discord_subscriber_count = len(assignments_df[assignments_df['username'] == 'Discord Event Subscriber'])
    print(f"\nFound {discord_subscriber_count} 'Discord Event Subscriber' entries to update")
    
    # Update the usernames
    for idx, row in assignments_df.iterrows():
        if row['username'] == 'Discord Event Subscriber':
            user_id = str(row['user_id'])
            if user_id in user_lookup:
                assignments_df.at[idx, 'username'] = user_lookup[user_id]
                updates_made += 1
    
    print(f"Updated {updates_made} usernames")
    
    # Save the updated file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f'user_role_assignments_FINAL_V3_{timestamp}.csv')
    assignments_df.to_csv(output_path, index=False)
    
    print(f"\n[SUCCESS] Saved updated assignments to: {output_path}")
    
    # Show some statistics
    print("\nFinal Statistics:")
    print(f"  Total assignments: {len(assignments_df)}")
    print(f"  Unique users: {len(assignments_df['user_id'].unique())}")
    print(f"  Unique roles: {len(assignments_df['role_id'].unique())}")
    
    # Show remaining generic usernames (if any)
    remaining_generic = assignments_df[assignments_df['username'] == 'Discord Event Subscriber']
    if len(remaining_generic) > 0:
        print(f"\n[WARNING] {len(remaining_generic)} entries still have 'Discord Event Subscriber' username")
        print("   These users were not found in the member list")
    
    return assignments_df

if __name__ == "__main__":
    update_discord_event_subscriber_usernames()