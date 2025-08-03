import os
import pandas as pd
import glob

OUTPUT_DIR = 'outputs'

def summarize_final_assignments():
    """Show a summary of the final assignments before applying roles"""
    
    # Find the latest V3 file
    v3_files = glob.glob(os.path.join(OUTPUT_DIR, 'user_role_assignments_FINAL_V3_*.csv'))
    if v3_files:
        assignments_file = max(v3_files, key=os.path.getctime)
        print(f"Using: {os.path.basename(assignments_file)}")
    else:
        print("No V3 file found!")
        return
    
    # Load the assignments
    df = pd.read_csv(assignments_file)
    
    print("\n" + "="*80)
    print("FINAL ROLE ASSIGNMENT SUMMARY")
    print("="*80)
    
    print(f"\nTotal assignments to make: {len(df)}")
    print(f"Unique users: {len(df['user_id'].unique())}")
    print(f"Unique roles: {len(df['role_id'].unique())}")
    
    # Show breakdown by data source
    print("\nBreakdown by data source:")
    print(f"  - ScheduleBot events: {df['schedule_bot_events'].sum()}")
    print(f"  - Discord scheduled events: {df['discord_scheduled_events'].sum()}")
    print(f"  - Manual interest events: {df['manual_interest_events'].sum()}")
    
    # Show top roles by user count
    print("\nTop 10 roles by user count:")
    print("-" * 50)
    role_counts = df.groupby('role_name')['user_id'].nunique().sort_values(ascending=False).head(10)
    for role, count in role_counts.items():
        print(f"  {role:30} {count:3} users")
    
    # Show users with most role assignments
    print("\nUsers with most role assignments (top 10):")
    print("-" * 50)
    user_counts = df.groupby('username')['role_id'].count().sort_values(ascending=False).head(10)
    for username, count in user_counts.items():
        print(f"  {username:30} {count:2} roles")
    
    # Check for any remaining generic usernames
    generic_users = df[df['username'] == 'Discord Event Subscriber']
    if len(generic_users) > 0:
        print(f"\n[WARNING] {len(generic_users)} assignments still have generic 'Discord Event Subscriber' username")
        print("These users were not found in the member list and may fail during role application")
    
    # Show test vs production breakdown
    print("\n" + "="*80)
    print("READY FOR ROLE APPLICATION")
    print("="*80)
    print("\nNext steps:")
    print("1. Test on BASIC's Creations (ID: 1249723747896918109)")
    print("   python apply_roles_final.py test")
    print("2. If successful, apply to The Faceless (ID: 480695542155051010)")
    print("   python apply_roles_final.py production-dry")
    print("   python apply_roles_final.py production-apply")

if __name__ == "__main__":
    summarize_final_assignments()