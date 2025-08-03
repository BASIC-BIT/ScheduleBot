import os
import pandas as pd

OUTPUT_DIR = 'outputs'

def summarize_fixed_assignments():
    """Show summary of the fixed assignments"""
    
    fixed_file = 'outputs/user_role_assignments_FIXED_20250802_223320.csv'
    
    print(f"Loading: {os.path.basename(fixed_file)}")
    df = pd.read_csv(fixed_file)
    
    print("\n" + "="*80)
    print("FIXED ROLE ASSIGNMENT SUMMARY")
    print("="*80)
    
    print(f"\nTotal assignments: {len(df)}")
    print(f"Unique users: {len(df['user_id'].unique())}")
    print(f"Unique roles: {len(df['role_id'].unique())}")
    
    # Verify no duplicate user IDs per username
    print("\nData Integrity Check:")
    print("-"*50)
    
    # Check for usernames with multiple IDs
    username_id_counts = df.groupby('username')['user_id'].nunique()
    multi_id_users = username_id_counts[username_id_counts > 1]
    
    if len(multi_id_users) == 0:
        print("[OK] No users have multiple IDs - data is clean!")
    else:
        print(f"[!] Found {len(multi_id_users)} users with multiple IDs:")
        for username, count in multi_id_users.items():
            ids = df[df['username'] == username]['user_id'].unique()
            print(f"    {username}: {ids}")
    
    # Show breakdown by data source
    print("\nAssignments by data source:")
    print(f"  - ScheduleBot only: {len(df[(df['schedule_bot_events'] > 0) & (df['discord_scheduled_events'] == 0) & (df['manual_interest_events'] == 0)])}")
    print(f"  - Discord scheduled only: {len(df[(df['schedule_bot_events'] == 0) & (df['discord_scheduled_events'] > 0) & (df['manual_interest_events'] == 0)])}")
    print(f"  - Manual interests only: {len(df[(df['schedule_bot_events'] == 0) & (df['discord_scheduled_events'] == 0) & (df['manual_interest_events'] > 0)])}")
    print(f"  - Combined sources: {len(df[(df['schedule_bot_events'] > 0) | (df['discord_scheduled_events'] > 0) | (df['manual_interest_events'] > 0)]) - len(df[(df['schedule_bot_events'] > 0) & (df['discord_scheduled_events'] == 0) & (df['manual_interest_events'] == 0)]) - len(df[(df['schedule_bot_events'] == 0) & (df['discord_scheduled_events'] > 0) & (df['manual_interest_events'] == 0)]) - len(df[(df['schedule_bot_events'] == 0) & (df['discord_scheduled_events'] == 0) & (df['manual_interest_events'] > 0)])}")
    
    # Top roles
    print("\nTop 15 roles by user count:")
    print("-"*50)
    role_counts = df.groupby('role_name')['user_id'].nunique().sort_values(ascending=False).head(15)
    for role, count in role_counts.items():
        print(f"  {role:30} {count:3} users")
    
    # Verify BASIC user
    print("\nSpotlight on BASIC:")
    print("-"*50)
    basic_assignments = df[df['username'] == 'basic_bit']
    if len(basic_assignments) > 0:
        basic_id = basic_assignments['user_id'].iloc[0]
        print(f"  Username: basic_bit")
        print(f"  User ID: {basic_id}")
        print(f"  Total roles: {len(basic_assignments)}")
        print(f"  Total events attended: {basic_assignments['schedule_bot_events'].sum() + basic_assignments['discord_scheduled_events'].sum() + basic_assignments['manual_interest_events'].sum()}")
    
    print("\n" + "="*80)
    print("READY FOR SAFE APPLICATION")
    print("="*80)

if __name__ == "__main__":
    summarize_fixed_assignments()