import pandas as pd
import os
from datetime import datetime

OUTPUT_DIR = 'outputs'

def fix_dj_and_missing_roles():
    """Fix DJ -> DJ Class and remove missing roles"""
    
    print("FIXING DJ ROLE AND REMOVING MISSING ROLES")
    print("="*80)
    
    # Load the authoritative assignments
    df = pd.read_csv(os.path.join(OUTPUT_DIR, 'user_role_assignments_AUTHORITATIVE_20250802_225050.csv'),
                     dtype={'role_id': str, 'user_id': str})
    
    print(f"Loaded {len(df)} assignments")
    
    # 1. Fix DJ -> DJ Class
    print("\n1. Updating DJ to DJ Class...")
    dj_mask = df['role_name'] == 'DJ'
    dj_count = dj_mask.sum()
    
    if dj_count > 0:
        # From our relevant_class_roles.csv, DJ Class has this ID
        df.loc[dj_mask, 'role_name'] = 'DJ Class'
        df.loc[dj_mask, 'role_id'] = '1392210777888526366'
        print(f"   Updated {dj_count} DJ assignments to DJ Class")
    
    # 2. Remove roles that don't exist on the server
    missing_roles = ['CHILL', 'Wotagei', 'Pole Dancing', 'Portal Posse', 'VR Fundamentals']
    
    print("\n2. Removing assignments for missing roles:")
    total_removed = 0
    
    for role in missing_roles:
        mask = df['role_name'] == role
        count = mask.sum()
        if count > 0:
            df = df[~mask]
            print(f"   Removed {count} {role} assignments")
            total_removed += count
    
    print(f"   Total removed: {total_removed}")
    
    # 3. Final validation
    print("\n3. Final Statistics:")
    print("-"*50)
    print(f"Total assignments: {len(df)} (was {len(df) + total_removed})")
    print(f"Unique users: {len(df['user_id'].unique())}")
    print(f"Unique roles: {len(df['role_id'].unique())}")
    
    # Show DJ Class stats
    dj_class_entries = df[df['role_name'] == 'DJ Class']
    print(f"\nDJ Class assignments: {len(dj_class_entries)}")
    
    # Save the fixed file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f'user_role_assignments_FINAL_FIXED_{timestamp}.csv')
    
    # Ensure dtypes are preserved
    df['role_id'] = df['role_id'].astype(str)
    df['user_id'] = df['user_id'].astype(str)
    
    df.to_csv(output_path, index=False)
    
    print(f"\n[SUCCESS] Saved fixed assignments to: {output_path}")
    
    # Show final role distribution
    print("\nFinal role distribution:")
    print("-"*50)
    role_counts = df.groupby(['role_name', 'role_id']).size().sort_values(ascending=False)
    for (role_name, role_id), count in role_counts.items():
        print(f"  {role_name:25} ({role_id}) - {count} users")
    
    # Check for any potential issues
    print("\nValidation checks:")
    print("-"*50)
    
    # Check if we still have any of the missing roles
    remaining_missing = df[df['role_name'].isin(missing_roles)]
    if len(remaining_missing) == 0:
        print("  ✓ All missing roles removed")
    else:
        print("  ✗ WARNING: Still have missing roles!")
    
    # Check DJ/DJ Class
    old_dj = df[df['role_name'] == 'DJ']
    new_dj = df[df['role_name'] == 'DJ Class']
    print(f"  ✓ DJ entries: {len(old_dj)} (should be 0)")
    print(f"  ✓ DJ Class entries: {len(new_dj)} (should be {dj_count})")
    
    return output_path

if __name__ == "__main__":
    fix_dj_and_missing_roles()