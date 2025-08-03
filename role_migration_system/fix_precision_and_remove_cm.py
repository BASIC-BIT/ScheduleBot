import pandas as pd
import os
from datetime import datetime

OUTPUT_DIR = 'outputs'

def fix_precision_and_remove_cm():
    """Fix role ID precision issues and remove Community Manager role"""
    
    print("FIXING ROLE ID PRECISION AND REMOVING COMMUNITY MANAGER")
    print("="*80)
    
    # Load ALL source files with proper dtype to preserve precision
    # 1. Load the event mappings with correct role IDs
    mappings = pd.read_csv(os.path.join(OUTPUT_DIR, 'event_role_mappings_reviewed.csv'), 
                          dtype={'matched_role_id': str})
    
    # Fix scientific notation in mappings
    print("Fixing scientific notation in mappings...")
    sci_notation_fixes = {
        '1.210262400985727e+18': '1210262400985727066',  # Community Manager
        '1.1630473108890624e+18': '1163047310889062420',  # DJ
        '1.3922102914370806e+18': '1392210291437080646',  # VIBE
        '1.3922105664075244e+18': '1392210566407524382',  # YOGA
        '1.3922109863871163e+18': '1392210986387116173',  # ASL Class
        '1.3922133304579236e+18': '1392213330457923594',  # Beyond Dance
        '1.3922105109712776e+18': '1392210510971277453',  # Vocal Class
        '1.3922107041400794e+18': '1392210704140079285',  # Breakin'
        '1.3922108864874458e+18': '1392210886487445655',  # Coding
        '1.3922104548222607e+18': '1392210454822260737',  # Esoterics
        '1.3922100759506493e+18': '1392210075950649415',  # Waltz
        '1.3922101169246743e+18': '1392210116924674212',  # Bachata
        '1.3922101704399299e+18': '1392210170439929877',  # Photography
        '1.392213840225112e+18': '1392213840225112155',   # Music Production
        '1.39221039322445e+18': '1392210393224450139',    # LOFT
        '1.3922096772821855e+18': '1392209677282185446',  # Animation Dance
        '1.3922138885225188e+18': '1392213888522518670',  # Sociology
        '1.3922113654557243e+18': '1392211365455724605',  # Meditation (manual interests)
        '1.3922111495958692e+18': '1392211149595869254',  # GOGO Dance
        '1.392210986387116e+18': '1392210986387116173',   # ASL Class
        '1.3922117143088376e+18': '1392211714308837507',  # Podcasts
    }
    
    for old_val, new_val in sci_notation_fixes.items():
        mappings.loc[mappings['matched_role_id'] == old_val, 'matched_role_id'] = new_val
    
    # Load role reference with correct IDs
    roles_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'relevant_class_roles.csv'),
                          dtype={'role_id': str})
    
    # Create a clean role lookup
    role_lookup = {}
    for _, role in roles_df.iterrows():
        role_lookup[role['role_name']] = str(role['role_id'])
    
    # Load the assignments file
    assignments = pd.read_csv(os.path.join(OUTPUT_DIR, 'user_role_assignments_PRODUCTION_READY_20250802_224433.csv'),
                             dtype={'role_id': str, 'user_id': str})
    
    print(f"\nLoaded {len(assignments)} assignments")
    
    # Remove Community Manager assignments
    cm_count = len(assignments[assignments['role_name'] == 'Community Manager'])
    assignments = assignments[assignments['role_name'] != 'Community Manager']
    print(f"Removed {cm_count} Community Manager assignments")
    
    # Fix role IDs using the role lookup
    print("\nFixing role IDs from source data...")
    fixes_made = 0
    
    for role_name, correct_id in role_lookup.items():
        mask = assignments['role_name'] == role_name
        if mask.sum() > 0:
            # Check if we need to fix
            current_ids = assignments.loc[mask, 'role_id'].unique()
            if len(current_ids) == 1 and current_ids[0] != correct_id:
                assignments.loc[mask, 'role_id'] = correct_id
                fixes_made += mask.sum()
                print(f"  Fixed {mask.sum()} entries for {role_name}: {current_ids[0]} -> {correct_id}")
    
    # Verify all role IDs are correct length (18-19 digits)
    print("\nVerifying role ID lengths...")
    role_id_lengths = assignments['role_id'].str.len().value_counts()
    print("Role ID length distribution:")
    for length, count in role_id_lengths.items():
        print(f"  {length} digits: {count} entries")
    
    # Final validation
    print("\nFinal validation:")
    print("-"*50)
    
    # Check for any truncated IDs
    short_ids = assignments[assignments['role_id'].str.len() < 18]
    if len(short_ids) > 0:
        print(f"WARNING: Found {len(short_ids)} entries with short role IDs!")
        print(short_ids[['role_name', 'role_id']].drop_duplicates())
    
    # Save the fixed file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f'user_role_assignments_FINAL_{timestamp}.csv')
    
    # Save with explicit string dtype
    assignments.to_csv(output_path, index=False)
    
    print(f"\n[SUCCESS] Saved final assignments to: {output_path}")
    
    # Statistics
    print("\nFinal Statistics:")
    print("-"*50)
    print(f"Total assignments: {len(assignments)}")
    print(f"Unique users: {len(assignments['user_id'].unique())}")
    print(f"Unique roles: {len(assignments['role_id'].unique())}")
    
    # Show all unique roles
    print("\nRoles to be assigned:")
    role_counts = assignments.groupby(['role_name', 'role_id']).size().sort_values(ascending=False)
    for (role_name, role_id), count in role_counts.items():
        print(f"  {role_name:25} (ID: {role_id}) - {count} users")
    
    return output_path

if __name__ == "__main__":
    fix_precision_and_remove_cm()