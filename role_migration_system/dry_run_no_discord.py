import pandas as pd
import os

OUTPUT_DIR = 'outputs'

def dry_run_no_discord():
    """Analyze what would happen without actually connecting to Discord"""
    
    print("DRY RUN ANALYSIS (No Discord Connection)")
    print("="*80)
    
    # Load assignments
    assignments_file = os.path.join(OUTPUT_DIR, 'user_role_assignments_AUTHORITATIVE_20250802_225050.csv')
    df = pd.read_csv(assignments_file, dtype={'role_id': str, 'user_id': str})
    
    print(f"\nTotal assignments to make: {len(df)}")
    print(f"Unique users: {len(df['user_id'].unique())}")
    print(f"Unique roles: {len(df['role_id'].unique())}")
    
    # Group by role
    print("\nAssignments by role:")
    print("-"*50)
    
    role_groups = df.groupby(['role_id', 'role_name']).size().sort_values(ascending=False)
    for (role_id, role_name), count in role_groups.items():
        print(f"{role_name:30} (ID: {role_id}) - {count} assignments")
    
    # Sample assignments
    print("\nSample assignments (first 10):")
    print("-"*50)
    
    for idx, row in df.head(10).iterrows():
        total_events = row['schedule_bot_events'] + row['discord_scheduled_events'] + row['manual_interest_events']
        print(f"{row['username']:20} -> {row['role_name']:20} ({total_events} events)")
    
    # Users with most roles
    print("\nUsers receiving most roles:")
    print("-"*50)
    
    user_role_counts = df.groupby(['user_id', 'username']).size().sort_values(ascending=False).head(10)
    for (user_id, username), count in user_role_counts.items():
        print(f"{username:20} (ID: {user_id}) - {count} roles")
    
    # Summary
    print("\n" + "="*80)
    print("READY TO APPLY")
    print("="*80)
    print("\nTo apply these roles, run:")
    print("  python apply_roles_final.py production-dry    # Verify first")
    print("  python apply_roles_final.py production-apply  # Actually apply")
    
    # Save a summary for reference
    summary_path = os.path.join(OUTPUT_DIR, 'dry_run_summary.txt')
    with open(summary_path, 'w') as f:
        f.write("ROLE MIGRATION DRY RUN SUMMARY\n")
        f.write("="*50 + "\n\n")
        f.write(f"Total assignments: {len(df)}\n")
        f.write(f"Unique users: {len(df['user_id'].unique())}\n")
        f.write(f"Unique roles: {len(df['role_id'].unique())}\n\n")
        f.write("Assignments by role:\n")
        for (role_id, role_name), count in role_groups.items():
            f.write(f"  {role_name}: {count}\n")
    
    print(f"\nSummary saved to: {summary_path}")

if __name__ == "__main__":
    dry_run_no_discord()