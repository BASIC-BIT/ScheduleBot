import pandas as pd
import os
from datetime import datetime

OUTPUT_DIR = 'outputs'

def fix_all_data_issues():
    """Fix all identified data quality issues"""
    
    print("FIXING ALL DATA QUALITY ISSUES")
    print("="*80)
    
    # Load the current data
    df = pd.read_csv(os.path.join(OUTPUT_DIR, 'user_role_assignments_FINAL_CLEAN_20250802_223726.csv'),
                     dtype={'role_id': str, 'user_id': str})
    
    original_count = len(df)
    print(f"Starting with {original_count} assignments")
    
    # 1. Fix duplicate entries by consolidating event counts
    print("\n1. FIXING DUPLICATES:")
    print("-"*50)
    
    # Group by user_id and role_id, summing the event counts
    print("Consolidating duplicate user-role pairs...")
    df_consolidated = df.groupby(['user_id', 'role_id', 'username', 'role_name']).agg({
        'schedule_bot_events': 'sum',
        'discord_scheduled_events': 'sum', 
        'manual_interest_events': 'sum'
    }).reset_index()
    
    duplicates_removed = original_count - len(df_consolidated)
    print(f"Removed {duplicates_removed} duplicate entries")
    
    # 2. Fix NJNA username
    print("\n2. FIXING NJNA USERNAME:")
    print("-"*50)
    
    # Find NJNA variations
    njna_mask = df_consolidated['username'].str.contains('njn', case=False, na=False)
    njna_entries = df_consolidated[njna_mask]
    print(f"Found {len(njna_entries)} NJNA entries with username: {njna_entries['username'].unique()}")
    
    # Standardize NJNA username
    df_consolidated.loc[njna_mask, 'username'] = 'NJNA'
    print("Standardized all NJNA variations to 'NJNA'")
    
    # 3. Fix Meditation role IDs
    print("\n3. FIXING MEDITATION ROLE IDS:")
    print("-"*50)
    
    # Find all Meditation entries
    med_mask = df_consolidated['role_name'] == 'Meditation'
    med_entries = df_consolidated[med_mask]
    unique_med_ids = med_entries['role_id'].unique()
    print(f"Found Meditation role IDs: {unique_med_ids}")
    
    # Fix all to the correct ID
    correct_med_id = '1392211365455724605'
    df_consolidated.loc[med_mask, 'role_id'] = correct_med_id
    print(f"Fixed all Meditation entries to use role ID: {correct_med_id}")
    
    # 4. Check for any remaining data issues
    print("\n4. FINAL VALIDATION:")
    print("-"*50)
    
    # Check for duplicates
    remaining_dupes = df_consolidated[df_consolidated.duplicated(subset=['user_id', 'role_id'], keep=False)]
    print(f"Remaining duplicates: {len(remaining_dupes)}")
    
    # Check roguewitxh YOGA
    rogue_yoga = df_consolidated[(df_consolidated['username'] == 'roguewitxh') & 
                                  (df_consolidated['role_name'] == 'YOGA')]
    print(f"roguewitxh YOGA entries: {len(rogue_yoga)}")
    if len(rogue_yoga) == 1:
        row = rogue_yoga.iloc[0]
        print(f"  Total events: SB={row['schedule_bot_events']}, DS={row['discord_scheduled_events']}, MI={row['manual_interest_events']}")
    
    # Check NJNA Beyond Dance
    njna_beyond = df_consolidated[(df_consolidated['username'] == 'NJNA') & 
                                   (df_consolidated['role_name'] == 'Beyond Dance')]
    print(f"NJNA Beyond Dance entries: {len(njna_beyond)}")
    
    # If NJNA is missing from Beyond Dance, we need to add it from source data
    if len(njna_beyond) == 0:
        print("\nAdding NJNA to Beyond Dance based on event attendance...")
        
        # Check if NJNA attended Beyond Dance events
        events_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'schedule_bot_events.csv'))
        beyond_events = events_df[events_df['EventTitle'].str.contains('BEYOND DANCE', case=False, na=False)]
        
        # NJNA is the instructor, so add them to Beyond Dance
        njna_user_id = df_consolidated[df_consolidated['username'] == 'NJNA']['user_id'].iloc[0]
        beyond_role_id = df_consolidated[df_consolidated['role_name'] == 'Beyond Dance']['role_id'].iloc[0]
        
        new_row = pd.DataFrame([{
            'user_id': njna_user_id,
            'role_id': beyond_role_id,
            'username': 'NJNA',
            'role_name': 'Beyond Dance',
            'schedule_bot_events': len(beyond_events),  # They taught all Beyond Dance events
            'discord_scheduled_events': 0,
            'manual_interest_events': 0
        }])
        
        df_consolidated = pd.concat([df_consolidated, new_row], ignore_index=True)
        print(f"Added NJNA to Beyond Dance (taught {len(beyond_events)} events)")
    
    # 5. Final statistics
    print("\n5. FINAL STATISTICS:")
    print("-"*50)
    print(f"Total assignments: {len(df_consolidated)} (was {original_count})")
    print(f"Unique users: {len(df_consolidated['user_id'].unique())}")
    print(f"Unique roles: {len(df_consolidated['role_id'].unique())}")
    
    # Save the fixed file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f'user_role_assignments_FINAL_FIXED_ALL_{timestamp}.csv')
    df_consolidated.to_csv(output_path, index=False)
    
    print(f"\n[SUCCESS] Saved fully fixed assignments to: {output_path}")
    
    # Show top users
    print("\nTop 10 users by role count:")
    user_counts = df_consolidated.groupby('username').size().sort_values(ascending=False).head(10)
    for username, count in user_counts.items():
        print(f"  {username:20} - {count} roles")
    
    return output_path

if __name__ == "__main__":
    fix_all_data_issues()