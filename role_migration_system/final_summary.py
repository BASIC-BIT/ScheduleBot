import pandas as pd
import os

OUTPUT_DIR = 'outputs'

def create_final_summary():
    """Create a final summary of what will be applied"""
    
    print("FINAL ROLE MIGRATION SUMMARY")
    print("="*80)
    
    # Load the final file
    df = pd.read_csv(os.path.join(OUTPUT_DIR, 'user_role_assignments_FINAL_FIXED_20250802_232315.csv'),
                     dtype={'role_id': str, 'user_id': str})
    
    print(f"\nTotal assignments to apply: {len(df)}")
    print(f"Unique users who will receive roles: {len(df['user_id'].unique())}")
    print(f"Unique roles to be assigned: {len(df['role_id'].unique())}")
    
    # Key changes made
    print("\nKey changes from original data:")
    print("-"*50)
    print("1. Removed Community Manager role (16 assignments)")
    print("2. Fixed duplicate user IDs (consolidated from 492 to 455)")
    print("3. Fixed role ID precision issues")
    print("4. Changed DJ to DJ Class (21 assignments)")
    print("5. Removed non-existent roles (35 assignments):")
    print("   - CHILL (1)")
    print("   - Wotagei (12)")
    print("   - Pole Dancing (8)")
    print("   - Portal Posse (12)")
    print("   - VR Fundamentals (2)")
    
    # Expected outcomes
    print("\nExpected outcomes:")
    print("-"*50)
    print("- Users will be automatically added to class/event roles based on their historical attendance")
    print("- This replaces the manual signup process with automatic role assignment")
    print("- Users can still leave roles if they no longer want notifications")
    
    # Top beneficiaries
    print("\nTop 10 users receiving most roles:")
    print("-"*50)
    user_counts = df.groupby(['username', 'user_id']).size().sort_values(ascending=False).head(10)
    for (username, user_id), count in user_counts.items():
        print(f"  {username:20} - {count} roles")
    
    # Role distribution
    print("\nRole distribution (all roles):")
    print("-"*50)
    role_counts = df.groupby('role_name').size().sort_values(ascending=False)
    for role, count in role_counts.items():
        print(f"  {role:25} - {count} users")
    
    # Save detailed report
    report_path = os.path.join(OUTPUT_DIR, 'final_migration_report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("FACELESS ROLE MIGRATION - FINAL REPORT\n")
        f.write("="*70 + "\n\n")
        f.write(f"Generated: {pd.Timestamp.now()}\n")
        f.write(f"Total assignments: {len(df)}\n")
        f.write(f"Unique users: {len(df['user_id'].unique())}\n")
        f.write(f"Unique roles: {len(df['role_id'].unique())}\n\n")
        
        f.write("ROLE ASSIGNMENTS BY USER\n")
        f.write("-"*70 + "\n")
        
        # Group by user and list their roles
        for (user_id, username), user_df in df.groupby(['user_id', 'username']):
            f.write(f"\n{username} (ID: {user_id}):\n")
            for _, row in user_df.iterrows():
                total_events = row['schedule_bot_events'] + row['discord_scheduled_events'] + row['manual_interest_events']
                f.write(f"  - {row['role_name']} ({total_events} events)\n")
    
    print(f"\nDetailed report saved to: {report_path}")
    
    print("\n" + "="*80)
    print("READY FOR PRODUCTION APPLICATION")
    print("="*80)
    print("\nTo apply these roles, run:")
    print("  python apply_roles_final.py production-dry")
    print("  python apply_roles_final.py production-apply")

if __name__ == "__main__":
    create_final_summary()