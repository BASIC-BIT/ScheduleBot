import pandas as pd
import os
from datetime import datetime

OUTPUT_DIR = 'outputs'

def fix_role_ids_to_current():
    """Update role IDs in assignments to match current server roles"""
    
    print("FIXING ROLE IDs TO MATCH CURRENT SERVER")
    print("="*80)
    
    # Load the production ready file
    df = pd.read_csv(os.path.join(OUTPUT_DIR, 'user_role_assignments_PRODUCTION_READY_20250802_224433.csv'),
                     dtype={'role_id': str, 'user_id': str})
    
    print(f"Loaded {len(df)} assignments")
    
    # Create mapping from old IDs to new IDs based on the fetch output
    role_id_mapping = {
        '1210262400985726976': '1210262400985727066',  # Community Manager
        '1392210170439929856': '1392210170439929877',  # Photography
        '1392210291437080576': '1392210291437080646',  # VIBE
        '1392210454822260736': '1392210454822260737',  # Esoterics
        '1392210510971277568': '1392210510971277453',  # Vocal Class
        '1392210566407524352': '1392210566407524382',  # YOGA
        '1392210886487445760': '1392210886487445655',  # Coding
        '1392210986387116032': '1392210986387116173',  # ASL Class
        '1392210986387116288': '1392210986387116173',  # ASL Class (duplicate)
        '1392211149595869184': '1392211149595869254',  # GOGO Dance
        '1392212045323304960': '1392212045323305020',  # Portal Posse
        '1392213840225112064': '1392213840225112155',  # Music Production
        '1392210704140079360': '1392210704140079285',  # Breakin'
        '1392210655318114304': '1392210655318114415',  # Wotagei
        '1163047310889062400': '1163047310889062420',  # DJ
        '1392209677282185728': '1392209677282185446',  # Animation Dance
        '1392210837330067712': '1392210837330067576',  # Blender/Unity
        '1392211204864344064': '1392211204864344175',  # Pole Dancing
        '1392213330457923584': '1392213330457923594',  # Beyond Dance
        '1392213888522518784': '1392213888522518670',  # Sociology
        '1392210170439930112': '1392210170439929877',  # Photography (duplicate)
        '1392209391872250112': '1392209391872250027',  # House Dance
        '1392210075950649088': '1392210075950649415',  # Waltz
        '1392210116924674304': '1392210116924674212',  # Bachata
        '1392210393224450048': '1392210393224450139',  # LOFT
        '1392211714308837632': '1392211714308837507',  # Podcasts
        '1392213286644219904': '1392213286644219994',  # VR Fundamentals
        '1392210349956009984': '1392210349956010075',  # CHILL
        '1392211365455724544': '1392211365455724605',  # Meditation (already fixed)
        '1392211365455724605': '1392211365455724605',  # Meditation (correct)
    }
    
    # Apply the mapping
    print("\nApplying role ID fixes...")
    fixes_made = 0
    
    for old_id, new_id in role_id_mapping.items():
        mask = df['role_id'] == old_id
        count = mask.sum()
        if count > 0:
            df.loc[mask, 'role_id'] = new_id
            fixes_made += count
            role_name = df.loc[mask, 'role_name'].iloc[0]
            print(f"  Fixed {count} entries for {role_name}: {old_id} -> {new_id}")
    
    print(f"\nTotal fixes made: {fixes_made}")
    
    # Check for any remaining unmapped role IDs
    current_roles = pd.read_csv(os.path.join(OUTPUT_DIR, 'production_roles_current_20250802_224649.csv'))
    current_role_ids = set(current_roles['role_id'].astype(str))
    
    our_role_ids = set(df['role_id'].unique())
    unmapped = our_role_ids - current_role_ids
    
    if unmapped:
        print(f"\nWARNING: {len(unmapped)} role IDs still not found on server:")
        for role_id in unmapped:
            role_name = df[df['role_id'] == role_id]['role_name'].iloc[0]
            print(f"  {role_name}: {role_id}")
    else:
        print("\n[OK] All role IDs now match current server roles!")
    
    # Save the fixed file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f'user_role_assignments_READY_TO_APPLY_{timestamp}.csv')
    df.to_csv(output_path, index=False)
    
    print(f"\n[SUCCESS] Saved fixed assignments to: {output_path}")
    print("\nThis file is ready for production application!")
    
    # Final statistics
    print("\nFinal Statistics:")
    print("-"*50)
    print(f"Total assignments: {len(df)}")
    print(f"Unique users: {len(df['user_id'].unique())}")
    print(f"Unique roles: {len(df['role_id'].unique())}")
    
    return output_path

if __name__ == "__main__":
    fix_role_ids_to_current()