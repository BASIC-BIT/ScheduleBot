import pandas as pd
import os

OUTPUT_DIR = 'outputs'

def investigate_basic_bit_issue():
    """Investigate the duplicate user ID issue for basic_bit"""
    
    # Load schedule bot events
    events_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'schedule_bot_events.csv'))
    
    print("Investigating basic_bit duplicate IDs issue...")
    print("="*80)
    
    # Find all events where basic_bit attended
    basic_events = events_df[events_df['AttendeeNames'].str.contains('basic_bit', case=False, na=False)]
    
    print(f"\nFound {len(basic_events)} events with 'basic_bit' in attendance")
    
    # Check a few specific events
    print("\nChecking first 5 events with basic_bit:")
    print("-"*80)
    
    for idx, event in basic_events.head(5).iterrows():
        print(f"\nEvent: {event['EventTitle']}")
        print(f"Date: {event['StartTime']}")
        
        names = str(event['AttendeeNames']).split(',')
        ids = str(event['AttendeeIds']).split(',')
        
        # Find basic_bit position
        basic_positions = []
        for i, name in enumerate(names):
            if 'basic_bit' in name.lower():
                basic_positions.append(i)
        
        print(f"Found basic_bit at position(s): {basic_positions}")
        
        for pos in basic_positions:
            if pos < len(ids):
                print(f"  Name: '{names[pos].strip()}' -> ID: '{ids[pos].strip()}'")
            else:
                print(f"  Name: '{names[pos].strip()}' -> ID: NOT FOUND (mismatch in array lengths)")
    
    # Check if the name/ID arrays have consistent lengths
    print("\n\nChecking for name/ID array length mismatches:")
    print("-"*80)
    
    mismatches = 0
    for idx, event in events_df.iterrows():
        if pd.notna(event['AttendeeNames']) and pd.notna(event['AttendeeIds']):
            names = str(event['AttendeeNames']).split(',')
            ids = str(event['AttendeeIds']).split(',')
            
            if len(names) != len(ids):
                mismatches += 1
                if mismatches <= 5:  # Show first 5 mismatches
                    print(f"\nMismatch in event: {event['EventTitle']}")
                    print(f"  Names count: {len(names)}, IDs count: {len(ids)}")
                    print(f"  Names: {event['AttendeeNames'][:100]}...")
                    print(f"  IDs: {str(event['AttendeeIds'])[:100]}...")
    
    print(f"\nTotal events with name/ID count mismatch: {mismatches} out of {len(events_df)}")
    
    # Check Discord member data
    print("\n\nChecking Discord member data for 'basic' usernames:")
    print("-"*80)
    
    members_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'faceless_members_basic.csv'))
    basic_members = members_df[members_df['username'].str.contains('basic', case=False, na=False)]
    
    print(f"Found {len(basic_members)} members with 'basic' in username:")
    for _, member in basic_members.iterrows():
        print(f"  {member['username']} (display: {member['display_name']}) -> ID: {member['user_id']}")
    
    # Check the actual BASIC user
    basic_user = members_df[members_df['user_id'] == 211750261922725888]
    if len(basic_user) > 0:
        print(f"\n\nThe real BASIC (ID: 211750261922725888):")
        print(f"  Username: {basic_user.iloc[0]['username']}")
        print(f"  Display name: {basic_user.iloc[0]['display_name']}")

if __name__ == "__main__":
    investigate_basic_bit_issue()