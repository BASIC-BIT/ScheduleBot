import pandas as pd
import os
from datetime import datetime

OUTPUT_DIR = 'outputs'

def final_fix_use_authoritative_ids():
    """Use only the authoritative role IDs from relevant_class_roles.csv"""
    
    print("FINAL FIX: Using Authoritative Role IDs")
    print("="*80)
    
    # Load the authoritative role data
    roles_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'relevant_class_roles.csv'),
                          dtype={'role_id': str})
    
    # Create role name to ID mapping
    role_name_to_id = {}
    for _, role in roles_df.iterrows():
        role_name_to_id[role['role_name']] = str(role['role_id'])
    
    print("Authoritative role mappings:")
    for name, rid in sorted(role_name_to_id.items()):
        print(f"  {name:25} -> {rid}")
    
    # Load assignments
    assignments = pd.read_csv(os.path.join(OUTPUT_DIR, 'user_role_assignments_PRODUCTION_READY_20250802_224433.csv'),
                             dtype={'role_id': str, 'user_id': str})
    
    print(f"\nLoaded {len(assignments)} assignments")
    
    # Remove Community Manager
    cm_mask = assignments['role_name'] == 'Community Manager'
    cm_count = cm_mask.sum()
    assignments = assignments[~cm_mask]
    print(f"Removed {cm_count} Community Manager assignments")
    
    # Fix ALL role IDs based on role name
    print("\nFixing ALL role IDs to authoritative values...")
    fixes_by_role = {}
    
    for idx, row in assignments.iterrows():
        role_name = row['role_name']
        current_id = row['role_id']
        
        if role_name in role_name_to_id:
            correct_id = role_name_to_id[role_name]
            if current_id != correct_id:
                assignments.at[idx, 'role_id'] = correct_id
                
                if role_name not in fixes_by_role:
                    fixes_by_role[role_name] = {'from': set(), 'to': correct_id, 'count': 0}
                fixes_by_role[role_name]['from'].add(current_id)
                fixes_by_role[role_name]['count'] += 1
        else:
            print(f"WARNING: Role '{role_name}' not found in authoritative list!")
    
    # Report fixes
    print("\nFixes applied:")
    for role_name, fix_info in sorted(fixes_by_role.items()):
        print(f"  {role_name}: {fix_info['count']} entries")
        for old_id in fix_info['from']:
            print(f"    {old_id} -> {fix_info['to']}")
    
    # Verify no duplicate user-role pairs
    print("\nChecking for duplicate user-role pairs...")
    dupes = assignments[assignments.duplicated(subset=['user_id', 'role_id'], keep=False)]
    if len(dupes) > 0:
        print(f"WARNING: Found {len(dupes)} duplicate entries. Consolidating...")
        # Consolidate by summing event counts
        assignments = assignments.groupby(['user_id', 'role_id', 'username', 'role_name'], as_index=False).agg({
            'schedule_bot_events': 'sum',
            'discord_scheduled_events': 'sum',
            'manual_interest_events': 'sum'
        })
        print(f"After consolidation: {len(assignments)} assignments")
    
    # Final validation
    print("\nFinal Validation:")
    print("-"*50)
    
    # Check all role IDs are correct length
    role_id_lengths = assignments['role_id'].str.len().value_counts()
    print("Role ID length distribution:")
    for length, count in sorted(role_id_lengths.items()):
        print(f"  {length} digits: {count} entries")
    
    # Verify ASL Class specifically
    asl_entries = assignments[assignments['role_name'] == 'ASL Class']
    asl_ids = asl_entries['role_id'].unique()
    print(f"\nASL Class check:")
    print(f"  Unique role IDs: {asl_ids}")
    print(f"  Total ASL assignments: {len(asl_entries)}")
    
    # Save the final file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f'user_role_assignments_AUTHORITATIVE_{timestamp}.csv')
    
    # Ensure role_id is saved as string
    assignments['role_id'] = assignments['role_id'].astype(str)
    assignments['user_id'] = assignments['user_id'].astype(str)
    
    assignments.to_csv(output_path, index=False)
    
    print(f"\n[SUCCESS] Saved authoritative assignments to: {output_path}")
    
    # Final statistics
    print("\nFinal Statistics:")
    print("-"*50)
    print(f"Total assignments: {len(assignments)}")
    print(f"Unique users: {len(assignments['user_id'].unique())}")
    print(f"Unique roles: {len(assignments['role_id'].unique())}")
    
    # Show role distribution
    print("\nRole distribution:")
    role_counts = assignments.groupby(['role_name', 'role_id']).size().sort_values(ascending=False)
    for (role_name, role_id), count in role_counts.items():
        print(f"  {role_name:25} ({role_id}) - {count} users")
    
    return output_path

if __name__ == "__main__":
    final_fix_use_authoritative_ids()