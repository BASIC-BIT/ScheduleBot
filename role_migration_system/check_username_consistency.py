import pandas as pd
import os
from collections import defaultdict

OUTPUT_DIR = 'outputs'

def check_username_consistency():
    """Check for users with multiple IDs in the ScheduleBot data"""
    
    # Load schedule bot events
    events_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'schedule_bot_events.csv'))
    
    # Build a mapping of username -> set of user IDs
    username_to_ids = defaultdict(set)
    
    print("Analyzing username consistency in ScheduleBot data...")
    print("="*80)
    
    total_attendances = 0
    
    for _, event in events_df.iterrows():
        if pd.notna(event['AttendeeNames']) and pd.notna(event['AttendeeIds']):
            names = str(event['AttendeeNames']).split(',')
            ids = str(event['AttendeeIds']).split(',')
            
            for i in range(min(len(names), len(ids))):
                name = names[i].strip().lower()
                user_id = ids[i].strip()
                
                if name and user_id and user_id.isdigit():
                    username_to_ids[name].add(user_id)
                    total_attendances += 1
    
    # Find usernames with multiple IDs
    inconsistent_users = {name: ids for name, ids in username_to_ids.items() if len(ids) > 1}
    
    print(f"Total unique usernames: {len(username_to_ids)}")
    print(f"Total attendances processed: {total_attendances}")
    print(f"Usernames with multiple IDs: {len(inconsistent_users)}")
    
    if inconsistent_users:
        print("\nTop 20 most inconsistent usernames:")
        print("-"*80)
        
        # Sort by number of different IDs
        sorted_users = sorted(inconsistent_users.items(), key=lambda x: len(x[1]), reverse=True)
        
        for i, (name, ids) in enumerate(sorted_users[:20]):
            print(f"\n{i+1}. '{name}' has {len(ids)} different IDs:")
            for user_id in list(ids)[:5]:  # Show first 5 IDs
                print(f"   - {user_id}")
            if len(ids) > 5:
                print(f"   ... and {len(ids) - 5} more")
    
    # Check if this affects our manual Discord interests data
    print("\n\nChecking if this affects manual Discord interests...")
    print("-"*80)
    
    manual_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'manual_discord_interests_with_ids.csv'))
    
    # Load the real member data
    members_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'faceless_members_basic.csv'))
    member_lookup = {str(row['user_id']): row['username'] for _, row in members_df.iterrows()}
    
    print("\nVerifying manual interest user IDs against current Discord data:")
    
    mismatches = 0
    for _, interest in manual_df.iterrows():
        if pd.notna(interest['user_id']):
            user_id = str(int(float(interest['user_id'])))
            if user_id in member_lookup:
                real_username = member_lookup[user_id]
                if real_username.lower() != interest['username'].lower():
                    if mismatches < 10:  # Show first 10
                        print(f"  Mismatch: '{interest['username']}' -> ID {user_id} (real username: '{real_username}')")
                    mismatches += 1
    
    print(f"\nTotal manual interest username/ID mismatches: {mismatches}")
    
    return inconsistent_users

if __name__ == "__main__":
    check_username_consistency()