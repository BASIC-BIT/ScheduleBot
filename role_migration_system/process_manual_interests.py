import pandas as pd
import json
import os

# Load the manual interest data
manual_interests = pd.read_csv('outputs/manual_discord_event_interests.csv')

# Load the event-to-role mappings
mappings = pd.read_csv('outputs/event_role_mappings_reviewed.csv')

# Create a structured format for each interested user
structured_data = []

for _, row in manual_interests.iterrows():
    event_name = row['event_name']
    usernames = row['interested_usernames'].split(',')
    
    # Clean up usernames
    usernames = [u.strip() for u in usernames]
    
    # Try to find a mapping for this event
    # First try exact match
    mapping = mappings[
        (mappings['event_title'] == event_name) & 
        (mappings['event_source'] == 'discord_scheduled')
    ]
    
    # If no exact match, try partial match
    if len(mapping) == 0:
        # Try to find similar event names
        for _, m in mappings.iterrows():
            if m['event_source'] == 'discord_scheduled':
                # Check if the event names are similar
                if event_name.lower() in m['event_title'].lower() or m['event_title'].lower() in event_name.lower():
                    mapping = mappings[mappings.index == m.name]
                    break
    
    if len(mapping) > 0 and not pd.isna(mapping.iloc[0]['matched_role_id']):
        role_id = mapping.iloc[0]['matched_role_id']
        role_name = mapping.iloc[0]['matched_role_name']
        
        for username in usernames:
            structured_data.append({
                'event_name': event_name,
                'username': username,
                'role_id': int(role_id),
                'role_name': role_name,
                'source': 'manual_discord_interests',
                'notes': row['notes']
            })
    else:
        print(f"No role mapping found for event: {event_name}")
        for username in usernames:
            structured_data.append({
                'event_name': event_name,
                'username': username,
                'role_id': None,
                'role_name': None,
                'source': 'manual_discord_interests',
                'notes': row['notes']
            })

# Convert to DataFrame
structured_df = pd.DataFrame(structured_data)

# Save the structured data
structured_df.to_csv('outputs/manual_discord_interests_structured.csv', index=False)

# Print summary
print("Manual Discord Interest Data Summary:")
print("=" * 60)
print(f"Total events processed: {len(manual_interests)}")
print(f"Total user interests recorded: {len(structured_df)}")
print(f"\nEvents with role mappings:")

mapped_events = structured_df[structured_df['role_id'].notna()].groupby(['event_name', 'role_name']).size().reset_index(name='interested_count')
for _, row in mapped_events.iterrows():
    print(f"  - {row['event_name']} -> {row['role_name']} ({row['interested_count']} interested)")

print(f"\nEvents WITHOUT role mappings:")
unmapped_events = structured_df[structured_df['role_id'].isna()]['event_name'].unique()
for event in unmapped_events:
    count = len(structured_df[structured_df['event_name'] == event])
    print(f"  - {event} ({count} interested)")

print(f"\nData saved to outputs/manual_discord_interests_structured.csv")