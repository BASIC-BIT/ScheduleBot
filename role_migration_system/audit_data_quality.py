import pandas as pd
import os

OUTPUT_DIR = 'outputs'

def audit_data_quality():
    """Comprehensive audit of data quality issues"""
    
    print("COMPREHENSIVE DATA QUALITY AUDIT")
    print("="*80)
    
    # Load the latest clean file
    df = pd.read_csv(os.path.join(OUTPUT_DIR, 'user_role_assignments_FINAL_CLEAN_20250802_223726.csv'))
    
    # 1. Check for duplicate user-role pairs
    print("\n1. DUPLICATE USER-ROLE ASSIGNMENTS:")
    print("-"*50)
    duplicates = df[df.duplicated(subset=['user_id', 'role_id'], keep=False)]
    if len(duplicates) > 0:
        print(f"Found {len(duplicates)} duplicate entries:")
        for _, row in duplicates.iterrows():
            print(f"  {row['username']} -> {row['role_name']}")
    else:
        print("No duplicates found")
    
    # 2. Check roguewitxh specifically
    print("\n2. ROGUEWITXH ANALYSIS:")
    print("-"*50)
    rogue_entries = df[df['username'].str.contains('rogue', case=False, na=False)]
    print(f"Found {len(rogue_entries)} entries for rogue* users:")
    for _, row in rogue_entries.iterrows():
        print(f"  {row['username']} -> {row['role_name']} (Events: SB={row['schedule_bot_events']}, DS={row['discord_scheduled_events']}, MI={row['manual_interest_events']})")
    
    # Check for YOGA specifically
    print("\nroguewitxh YOGA entries:")
    rogue_yoga = df[(df['username'].str.contains('rogue', case=False, na=False)) & (df['role_name'] == 'YOGA')]
    for _, row in rogue_yoga.iterrows():
        print(f"  ID: {row['user_id']}, Events: SB={row['schedule_bot_events']}, DS={row['discord_scheduled_events']}, MI={row['manual_interest_events']}")
    
    # 3. Check NJNA/Beyond Dance
    print("\n3. BEYOND DANCE ANALYSIS:")
    print("-"*50)
    beyond_entries = df[df['role_name'] == 'Beyond Dance']
    print(f"Total Beyond Dance assignments: {len(beyond_entries)}")
    print("Users assigned Beyond Dance role:")
    for _, row in beyond_entries.iterrows():
        print(f"  {row['username']}")
    
    # Check for NJNA in any role
    print("\nNJNA presence in data:")
    njna_entries = df[df['username'].str.contains('njna|njn', case=False, na=False)]
    if len(njna_entries) > 0:
        print("Found NJNA entries:")
        for _, row in njna_entries.iterrows():
            print(f"  {row['username']} -> {row['role_name']}")
    else:
        print("NJNA not found in assignments!")
    
    # 4. Meditation role ID analysis
    print("\n4. MEDITATION ROLE ID ANALYSIS:")
    print("-"*50)
    med_entries = df[df['role_name'] == 'Meditation']
    unique_med_ids = med_entries['role_id'].unique()
    print(f"Unique Meditation role IDs: {unique_med_ids}")
    print(f"Number of unique IDs: {len(unique_med_ids)}")
    
    # Check event mappings for Meditation
    mappings = pd.read_csv(os.path.join(OUTPUT_DIR, 'event_role_mappings_reviewed.csv'), dtype={'matched_role_id': str})
    med_mappings = mappings[mappings['matched_role_name'] == 'Meditation']
    print("\nMeditation mappings in event_role_mappings_reviewed.csv:")
    for _, row in med_mappings.iterrows():
        print(f"  Event: {row['event_title']} -> Role ID: {row['matched_role_id']}")
    
    # 5. Check manual interests data
    print("\n5. MANUAL INTERESTS DATA QUALITY:")
    print("-"*50)
    manual = pd.read_csv(os.path.join(OUTPUT_DIR, 'manual_discord_interests_with_ids.csv'))
    
    # Check for NJNA in manual data
    manual_njna = manual[manual['username'].str.contains('NJN', case=False, na=False)]
    print(f"NJNA in manual interests: {len(manual_njna)} entries")
    if len(manual_njna) > 0:
        for _, row in manual_njna.iterrows():
            try:
                print(f"  Event: {row['event_name']} -> Username: {row['username']}")
            except:
                print(f"  Event: [Unicode Error] -> Username: {row['username'].encode('ascii', 'ignore').decode()}")
    
    # 6. Check source data integrity
    print("\n6. SOURCE DATA INTEGRITY:")
    print("-"*50)
    
    # Check Beyond Dance in ScheduleBot events
    events_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'schedule_bot_events.csv'))
    beyond_events = events_df[events_df['EventTitle'].str.contains('Beyond Dance', case=False, na=False)]
    print(f"\nBeyond Dance events in ScheduleBot: {len(beyond_events)}")
    for _, event in beyond_events.head(3).iterrows():
        print(f"  {event['EventTitle']} - Attendees: {event['AttendeeNames']}")
    
    # 7. Username variations
    print("\n7. USERNAME VARIATIONS:")
    print("-"*50)
    # Group by lowercase username to find variations
    df['username_lower'] = df['username'].str.lower()
    username_groups = df.groupby('username_lower')['username'].unique()
    variations = {k: v for k, v in username_groups.items() if len(v) > 1}
    
    if variations:
        print("Found username variations:")
        for lower, variants in list(variations.items())[:10]:
            print(f"  {lower}: {variants}")
    
    # 8. Role name consistency
    print("\n8. ROLE NAME CONSISTENCY:")
    print("-"*50)
    role_id_groups = df.groupby('role_id')['role_name'].unique()
    inconsistent_roles = {k: v for k, v in role_id_groups.items() if len(v) > 1}
    
    if inconsistent_roles:
        print("Found inconsistent role names for same ID:")
        for role_id, names in inconsistent_roles.items():
            print(f"  Role ID {role_id}: {names}")
    
    return df

if __name__ == "__main__":
    audit_data_quality()