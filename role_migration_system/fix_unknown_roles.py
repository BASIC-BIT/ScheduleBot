import pandas as pd
import os
from datetime import datetime

OUTPUT_DIR = 'outputs'

def fix_unknown_roles():
    """Fix the Unknown Role entries that are actually Meditation role"""
    
    print("Fixing Unknown Role entries...")
    print("="*80)
    
    # Load the latest FIXED file
    import glob
    fixed_files = glob.glob(os.path.join(OUTPUT_DIR, 'user_role_assignments_FIXED_*.csv'))
    if not fixed_files:
        print("No FIXED file found!")
        return
    
    assignments_file = max(fixed_files, key=os.path.getctime)
    print(f"Processing: {os.path.basename(assignments_file)}")
    
    # Load with proper dtype to preserve full role IDs
    df = pd.read_csv(assignments_file, dtype={'role_id': str, 'user_id': str})
    
    # Find Unknown Role entries
    unknown_mask = df['role_name'].str.contains('Unknown', case=False, na=False)
    unknown_entries = df[unknown_mask]
    
    print(f"\nFound {len(unknown_entries)} Unknown Role entries")
    
    # The incorrect role ID that was truncated
    wrong_id = '1392211365455724288'
    # The correct Meditation role ID
    correct_id = '1392211365455724605'
    
    # Check if all unknown entries have the same wrong ID
    unique_unknown_ids = unknown_entries['role_id'].unique()
    print(f"Unique Unknown role IDs: {unique_unknown_ids}")
    
    if len(unique_unknown_ids) == 1 and unique_unknown_ids[0] == wrong_id:
        print(f"\nAll Unknown entries have ID {wrong_id}")
        print("This appears to be the truncated Meditation role ID")
        print(f"Fixing to correct Meditation role ID: {correct_id}")
        
        # Fix the role ID and name
        df.loc[unknown_mask, 'role_id'] = correct_id
        df.loc[unknown_mask, 'role_name'] = 'Meditation'
        
        print(f"\nFixed {len(unknown_entries)} entries from Unknown Role to Meditation")
    else:
        print("\nUnexpected Unknown role IDs found. Manual review needed.")
        return
    
    # Save the fixed file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f'user_role_assignments_FINAL_CLEAN_{timestamp}.csv')
    df.to_csv(output_path, index=False)
    
    print(f"\n[SUCCESS] Saved cleaned assignments to: {output_path}")
    
    # Show final statistics
    print("\nFinal Statistics:")
    print("-"*80)
    print(f"Total assignments: {len(df)}")
    print(f"Unique users: {len(df['user_id'].unique())}")
    print(f"Unique roles: {len(df['role_id'].unique())}")
    
    # Verify no more unknown roles
    remaining_unknown = df[df['role_name'].str.contains('Unknown', case=False, na=False)]
    if len(remaining_unknown) == 0:
        print("\n[OK] No Unknown roles remaining - data is clean!")
    else:
        print(f"\n[WARNING] Still have {len(remaining_unknown)} Unknown role entries")
    
    # Show Meditation role stats
    meditation_entries = df[df['role_name'] == 'Meditation']
    print(f"\nMeditation role now has {len(meditation_entries)} assignments for {len(meditation_entries['user_id'].unique())} users")
    
    return output_path

if __name__ == "__main__":
    fix_unknown_roles()