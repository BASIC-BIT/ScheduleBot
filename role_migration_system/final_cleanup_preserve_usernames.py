import pandas as pd
import os
from datetime import datetime

OUTPUT_DIR = 'outputs'

def final_cleanup_preserve_usernames():
    """Final cleanup to ensure no duplicates remain, preserving original usernames"""
    
    print("FINAL DATA CLEANUP (Preserving Original Usernames)")
    print("="*80)
    
    # Load the CLEAN file (before NJNA name change)
    df = pd.read_csv(os.path.join(OUTPUT_DIR, 'user_role_assignments_FINAL_CLEAN_20250802_223726.csv'),
                     dtype={'role_id': str, 'user_id': str})
    
    print(f"Starting with {len(df)} assignments")
    
    # First, ensure all Meditation entries use the correct role ID
    print("\nFixing Meditation role IDs...")
    med_mask = df['role_name'] == 'Meditation'
    correct_med_id = '1392211365455724605'
    df.loc[med_mask, 'role_id'] = correct_med_id
    print(f"Fixed all Meditation entries to use role ID: {correct_med_id}")
    
    # Remove ALL duplicates by consolidating event counts
    print("\nConsolidating duplicate entries...")
    
    # Group by key fields and sum the event counts
    df_consolidated = df.groupby(['user_id', 'role_id', 'username', 'role_name'], as_index=False).agg({
        'schedule_bot_events': 'sum',
        'discord_scheduled_events': 'sum', 
        'manual_interest_events': 'sum'
    })
    
    duplicates_removed = len(df) - len(df_consolidated)
    print(f"Removed {duplicates_removed} duplicate entries")
    
    # Verify no duplicates remain
    remaining_dupes = df_consolidated[df_consolidated.duplicated(subset=['user_id', 'role_id'], keep=False)]
    print(f"\nDuplicates check: {len(remaining_dupes)} remaining (should be 0)")
    
    # Add NJNA to Beyond Dance if missing (but keep original username)
    njna_beyond = df_consolidated[(df_consolidated['username'] == 'njnagrimsdottir') & 
                                   (df_consolidated['role_name'] == 'Beyond Dance')]
    
    if len(njna_beyond) == 0:
        print("\nAdding njnagrimsdottir to Beyond Dance based on teaching events...")
        
        # Get NJNA's user ID
        njna_entries = df_consolidated[df_consolidated['username'] == 'njnagrimsdottir']
        if len(njna_entries) > 0:
            njna_user_id = njna_entries.iloc[0]['user_id']
            beyond_role_id = df_consolidated[df_consolidated['role_name'] == 'Beyond Dance'].iloc[0]['role_id']
            
            # Count Beyond Dance events from source
            events_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'schedule_bot_events.csv'))
            beyond_events = events_df[events_df['EventTitle'].str.contains('BEYOND DANCE', case=False, na=False)]
            
            new_row = pd.DataFrame([{
                'user_id': njna_user_id,
                'role_id': beyond_role_id,
                'username': 'njnagrimsdottir',  # Keep original username
                'role_name': 'Beyond Dance',
                'schedule_bot_events': len(beyond_events),
                'discord_scheduled_events': 0,
                'manual_interest_events': 0
            }])
            
            df_consolidated = pd.concat([df_consolidated, new_row], ignore_index=True)
            print(f"Added njnagrimsdottir to Beyond Dance (taught {len(beyond_events)} events)")
    
    # Final validation checks
    print("\nFINAL VALIDATION:")
    print("-"*50)
    
    # Check key users
    validations = [
        ('roguewitxh', 'YOGA'),
        ('njnagrimsdottir', 'Beyond Dance'),
        ('basic_bit', 'Meditation'),
        ('basic_bit', 'DJ')
    ]
    
    for username, role_name in validations:
        entries = df_consolidated[(df_consolidated['username'] == username) & (df_consolidated['role_name'] == role_name)]
        if len(entries) == 1:
            row = entries.iloc[0]
            total = row['schedule_bot_events'] + row['discord_scheduled_events'] + row['manual_interest_events']
            print(f"[OK] {username} -> {role_name}: {len(entries)} entry, {total} total events")
        elif len(entries) == 0:
            print(f"[X] {username} -> {role_name}: NOT FOUND")
        else:
            print(f"[X] {username} -> {role_name}: {len(entries)} entries (DUPLICATE!)")
    
    # Check Meditation role consistency
    med_entries = df_consolidated[df_consolidated['role_name'] == 'Meditation']
    unique_med_ids = med_entries['role_id'].unique()
    print(f"\nMeditation role IDs: {unique_med_ids} (should be 1 ID)")
    
    # Final statistics
    print("\nFINAL STATISTICS:")
    print("-"*50)
    print(f"Total assignments: {len(df_consolidated)}")
    print(f"Unique users: {len(df_consolidated['user_id'].unique())}")
    print(f"Unique roles: {len(df_consolidated['role_id'].unique())}")
    
    # Show njnagrimsdottir's roles
    njna_all = df_consolidated[df_consolidated['username'] == 'njnagrimsdottir']
    print(f"\nnjnagrimsdottir has {len(njna_all)} roles:")
    for _, row in njna_all.iterrows():
        print(f"  - {row['role_name']}")
    
    # Top roles
    print("\nTop 10 roles by user count:")
    role_counts = df_consolidated.groupby('role_name')['user_id'].nunique().sort_values(ascending=False).head(10)
    for role, count in role_counts.items():
        print(f"  {role:25} - {count} users")
    
    # Save the final clean file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f'user_role_assignments_PRODUCTION_READY_{timestamp}.csv')
    df_consolidated.to_csv(output_path, index=False)
    
    print(f"\n[SUCCESS] Saved PRODUCTION READY assignments to: {output_path}")
    print("\nThis file is ready for production deployment!")
    
    return output_path

if __name__ == "__main__":
    final_cleanup_preserve_usernames()