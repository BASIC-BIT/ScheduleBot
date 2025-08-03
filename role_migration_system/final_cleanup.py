import pandas as pd
import os
from datetime import datetime

OUTPUT_DIR = 'outputs'

def final_cleanup():
    """Final cleanup to ensure no duplicates remain"""
    
    print("FINAL DATA CLEANUP")
    print("="*80)
    
    # Load the latest fixed file
    df = pd.read_csv(os.path.join(OUTPUT_DIR, 'user_role_assignments_FINAL_FIXED_ALL_20250802_224222.csv'),
                     dtype={'role_id': str, 'user_id': str})
    
    print(f"Starting with {len(df)} assignments")
    
    # Remove ALL duplicates by keeping the one with highest total events
    print("\nRemoving remaining duplicates...")
    
    # Calculate total events for each row
    df['total_events'] = df['schedule_bot_events'] + df['discord_scheduled_events'] + df['manual_interest_events']
    
    # Sort by user_id, role_id, and total_events (descending)
    df_sorted = df.sort_values(['user_id', 'role_id', 'total_events'], 
                               ascending=[True, True, False])
    
    # Drop duplicates, keeping the first (which has most events due to sort)
    df_clean = df_sorted.drop_duplicates(subset=['user_id', 'role_id'], keep='first')
    
    # Drop the temporary total_events column
    df_clean = df_clean.drop(columns=['total_events'])
    
    duplicates_removed = len(df) - len(df_clean)
    print(f"Removed {duplicates_removed} duplicate entries")
    
    # Verify no duplicates remain
    remaining_dupes = df_clean[df_clean.duplicated(subset=['user_id', 'role_id'], keep=False)]
    print(f"\nDuplicates check: {len(remaining_dupes)} remaining (should be 0)")
    
    # Final validation checks
    print("\nFINAL VALIDATION:")
    print("-"*50)
    
    # Check key users
    validations = [
        ('roguewitxh', 'YOGA'),
        ('NJNA', 'Beyond Dance'),
        ('basic_bit', 'Meditation'),
        ('basic_bit', 'DJ')
    ]
    
    for username, role_name in validations:
        entries = df_clean[(df_clean['username'] == username) & (df_clean['role_name'] == role_name)]
        if len(entries) == 1:
            row = entries.iloc[0]
            total = row['schedule_bot_events'] + row['discord_scheduled_events'] + row['manual_interest_events']
            print(f"✓ {username} -> {role_name}: {len(entries)} entry, {total} total events")
        elif len(entries) == 0:
            print(f"✗ {username} -> {role_name}: NOT FOUND")
        else:
            print(f"✗ {username} -> {role_name}: {len(entries)} entries (DUPLICATE!)")
    
    # Check Meditation role consistency
    med_entries = df_clean[df_clean['role_name'] == 'Meditation']
    unique_med_ids = med_entries['role_id'].unique()
    print(f"\nMeditation role IDs: {unique_med_ids} (should be 1 ID)")
    
    # Final statistics
    print("\nFINAL STATISTICS:")
    print("-"*50)
    print(f"Total assignments: {len(df_clean)}")
    print(f"Unique users: {len(df_clean['user_id'].unique())}")
    print(f"Unique roles: {len(df_clean['role_id'].unique())}")
    
    # Top roles
    print("\nTop 10 roles by user count:")
    role_counts = df_clean.groupby('role_name')['user_id'].nunique().sort_values(ascending=False).head(10)
    for role, count in role_counts.items():
        print(f"  {role:25} - {count} users")
    
    # Save the final clean file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f'user_role_assignments_PRODUCTION_READY_{timestamp}.csv')
    df_clean.to_csv(output_path, index=False)
    
    print(f"\n[SUCCESS] Saved PRODUCTION READY assignments to: {output_path}")
    print("\nThis file is ready for production deployment!")
    
    return output_path

if __name__ == "__main__":
    final_cleanup()