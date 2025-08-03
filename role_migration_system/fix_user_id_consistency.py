import pandas as pd
import os
from datetime import datetime

OUTPUT_DIR = 'outputs'

def fix_user_id_consistency():
    """Fix the user ID consistency issue by using only valid Discord member IDs"""
    
    print("Fixing user ID consistency issues...")
    print("="*80)
    
    # Load current Discord members - this is our source of truth
    members_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'faceless_members_basic.csv'))
    
    # Create lookup dictionaries
    username_to_id = {}
    id_to_username = {}
    
    for _, member in members_df.iterrows():
        user_id = str(member['user_id'])
        username = member['username'].lower()
        display_name = str(member['display_name']).lower() if pd.notna(member['display_name']) else username
        
        # Map by username
        username_to_id[username] = user_id
        # Also map by display name if different
        if display_name != username:
            username_to_id[display_name] = user_id
        
        # Reverse mapping
        id_to_username[user_id] = member['username']
    
    print(f"Loaded {len(members_df)} valid Discord members")
    
    # Load the latest assignments file
    import glob
    v3_files = glob.glob(os.path.join(OUTPUT_DIR, 'user_role_assignments_FINAL_V3_*.csv'))
    if not v3_files:
        print("No V3 file found!")
        return
    
    assignments_file = max(v3_files, key=os.path.getctime)
    print(f"\nProcessing: {os.path.basename(assignments_file)}")
    
    assignments_df = pd.read_csv(assignments_file)
    original_count = len(assignments_df)
    
    # Track fixes
    fixed_count = 0
    removed_count = 0
    already_valid_count = 0
    
    # Process each assignment
    valid_assignments = []
    
    for _, assignment in assignments_df.iterrows():
        user_id = str(assignment['user_id'])
        username = assignment['username']
        
        # Check if the user ID is valid (exists in current Discord members)
        if user_id in id_to_username:
            # Valid ID - keep assignment with correct username
            assignment_copy = assignment.copy()
            assignment_copy['username'] = id_to_username[user_id]
            assignment_copy['fix_status'] = 'valid'
            valid_assignments.append(assignment_copy)
            already_valid_count += 1
        else:
            # Invalid ID - try to find correct ID by username
            username_lower = username.lower()
            
            if username_lower in username_to_id:
                # Found correct ID by username
                assignment_copy = assignment.copy()
                assignment_copy['user_id'] = username_to_id[username_lower]
                assignment_copy['username'] = id_to_username[username_to_id[username_lower]]
                assignment_copy['fix_status'] = 'fixed_by_username'
                valid_assignments.append(assignment_copy)
                fixed_count += 1
            else:
                # Can't fix - user not found in current Discord
                removed_count += 1
                if removed_count <= 10:  # Show first 10 removals
                    print(f"  Removing: {username} (ID: {user_id}) - not found in Discord")
    
    # Create new DataFrame with valid assignments
    fixed_df = pd.DataFrame(valid_assignments)
    
    # Remove duplicate user-role pairs (keep the one with most events)
    print("\nRemoving duplicate user-role assignments...")
    before_dedup = len(fixed_df)
    
    # Sort by event count descending, then keep first of each user-role pair
    fixed_df = fixed_df.sort_values(
        ['user_id', 'role_id', 'schedule_bot_events', 'discord_scheduled_events', 'manual_interest_events'],
        ascending=[True, True, False, False, False]
    )
    fixed_df = fixed_df.drop_duplicates(subset=['user_id', 'role_id'], keep='first')
    
    duplicates_removed = before_dedup - len(fixed_df)
    
    # Remove the fix_status column before saving
    fixed_df = fixed_df.drop(columns=['fix_status'])
    
    # Save the fixed assignments
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f'user_role_assignments_FIXED_{timestamp}.csv')
    fixed_df.to_csv(output_path, index=False)
    
    # Summary
    print("\n" + "="*80)
    print("FIX SUMMARY:")
    print("="*80)
    print(f"Original assignments: {original_count}")
    print(f"Already valid: {already_valid_count}")
    print(f"Fixed by username lookup: {fixed_count}")
    print(f"Removed (user not in Discord): {removed_count}")
    print(f"Duplicate assignments removed: {duplicates_removed}")
    print(f"Final assignments: {len(fixed_df)}")
    
    print(f"\n[SUCCESS] Fixed assignments saved to: {output_path}")
    
    # Show statistics for the fixed data
    print("\nFixed Data Statistics:")
    print("-"*80)
    print(f"Unique users: {len(fixed_df['user_id'].unique())}")
    print(f"Unique roles: {len(fixed_df['role_id'].unique())}")
    
    # Check for any remaining issues
    print("\nValidation Check:")
    # Check basic_bit
    basic_assignments = fixed_df[fixed_df['username'] == 'basic_bit']
    basic_ids = basic_assignments['user_id'].unique()
    print(f"basic_bit now has {len(basic_ids)} unique ID(s): {basic_ids}")
    
    # Top users by role count
    print("\nTop 10 users by role count (fixed data):")
    user_role_counts = fixed_df.groupby('username')['role_id'].count().sort_values(ascending=False).head(10)
    for username, count in user_role_counts.items():
        user_id = fixed_df[fixed_df['username'] == username]['user_id'].iloc[0]
        print(f"  {username:20} (ID: {user_id}) - {count} roles")
    
    return output_path

if __name__ == "__main__":
    fix_user_id_consistency()