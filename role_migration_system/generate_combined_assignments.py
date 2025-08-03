import os
import pandas as pd
from datetime import datetime

OUTPUT_DIR = 'outputs'

def generate_user_role_assignments_with_manual():
    """
    Generate user-to-role assignments based on historical attendance data,
    Discord event subscribers, and manually collected Discord interests.
    """
    # Load all necessary data
    print("Loading data files...")
    
    # Load schedule bot events
    schedule_events_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'schedule_bot_events.csv'))
    print(f"  Loaded {len(schedule_events_df)} schedule bot events")
    
    # Load Discord scheduled events
    discord_events_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'discord_scheduled_events.csv'))
    print(f"  Loaded {len(discord_events_df)} Discord scheduled events")
    
    # Load reviewed mappings
    mappings_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'event_role_mappings_reviewed.csv'))
    print(f"  Loaded {len(mappings_df)} event-to-role mappings")
    
    # Load manual Discord interests with user IDs
    manual_interests_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'manual_discord_interests_with_ids.csv'))
    print(f"  Loaded {len(manual_interests_df)} manual interest records")
    
    # Dictionary to store user-role assignments
    user_role_assignments = {}
    
    print("\nProcessing Schedule Bot attendance data...")
    print("=" * 80)
    
    # Process schedule bot events
    schedule_bot_users = 0
    for _, event in schedule_events_df.iterrows():
        event_title = event['EventTitle']
        
        # Find the role mapping for this event
        mapping = mappings_df[
            (mappings_df['event_source'] == 'schedule_bot') & 
            (mappings_df['event_title'] == event_title)
        ]
        
        if len(mapping) == 0 or pd.isna(mapping.iloc[0]['matched_role_id']):
            continue
        
        role_id = int(mapping.iloc[0]['matched_role_id'])
        role_name = mapping.iloc[0]['matched_role_name']
        
        # Initialize role dict if needed
        if role_id not in user_role_assignments:
            user_role_assignments[role_id] = {}
        
        # Process attendees
        if pd.notna(event['AttendeeIds']) and event['AttendeeCount'] > 0:
            attendee_ids = str(event['AttendeeIds']).split(',')
            attendee_names = str(event['AttendeeNames']).split(',')
            
            for i, user_id in enumerate(attendee_ids):
                try:
                    user_id = int(user_id.strip())
                    username = attendee_names[i].strip() if i < len(attendee_names) else 'Unknown'
                    
                    if user_id not in user_role_assignments[role_id]:
                        user_role_assignments[role_id][user_id] = {
                            'username': username,
                            'sources': []
                        }
                        schedule_bot_users += 1
                    
                    user_role_assignments[role_id][user_id]['sources'].append({
                        'type': 'schedule_bot',
                        'event': event_title,
                        'date': str(event['StartTime'])
                    })
                except (ValueError, IndexError):
                    continue
    
    print(f"  Added {schedule_bot_users} unique user-role pairs from ScheduleBot")
    
    print("\nProcessing Discord scheduled event subscribers...")
    print("=" * 80)
    
    # Process Discord scheduled events
    discord_scheduled_users = 0
    for _, event in discord_events_df.iterrows():
        event_name = event['event_name']
        
        # Find the role mapping for this event
        mapping = mappings_df[
            (mappings_df['event_source'] == 'discord_scheduled') & 
            (mappings_df['event_title'] == event_name)
        ]
        
        if len(mapping) == 0 or pd.isna(mapping.iloc[0]['matched_role_id']):
            continue
        
        role_id = int(mapping.iloc[0]['matched_role_id'])
        role_name = mapping.iloc[0]['matched_role_name']
        
        # Initialize role dict if needed
        if role_id not in user_role_assignments:
            user_role_assignments[role_id] = {}
        
        # Process subscribers
        if pd.notna(event.get('subscriber_ids', [])) and event['subscriber_ids'] != '[]':
            try:
                subscriber_ids = eval(event['subscriber_ids']) if isinstance(event['subscriber_ids'], str) else event['subscriber_ids']
                
                for user_id in subscriber_ids:
                    try:
                        user_id = int(user_id)
                        
                        if user_id not in user_role_assignments[role_id]:
                            user_role_assignments[role_id][user_id] = {
                                'username': 'Discord Event Subscriber',
                                'sources': []
                            }
                            discord_scheduled_users += 1
                        
                        user_role_assignments[role_id][user_id]['sources'].append({
                            'type': 'discord_scheduled',
                            'event': event_name,
                            'date': str(event['start_time'])
                        })
                    except ValueError:
                        continue
            except:
                continue
    
    print(f"  Added {discord_scheduled_users} unique user-role pairs from Discord scheduled events")
    
    print("\nProcessing Manual Discord Interests...")
    print("=" * 80)
    
    # Process manual Discord interests
    manual_users_added = 0
    for _, interest in manual_interests_df.iterrows():
        if pd.notna(interest['user_id']) and pd.notna(interest['role_id']):
            try:
                user_id = int(interest['user_id'])
                role_id = int(interest['role_id'])
                role_name = interest['role_name']
                
                # Initialize role dict if needed
                if role_id not in user_role_assignments:
                    user_role_assignments[role_id] = {}
                
                # Add user if not already there
                if user_id not in user_role_assignments[role_id]:
                    user_role_assignments[role_id][user_id] = {
                        'username': interest['username'],
                        'sources': []
                    }
                    manual_users_added += 1
                
                # Add the manual interest as a source
                user_role_assignments[role_id][user_id]['sources'].append({
                    'type': 'manual_discord_interest',
                    'event': interest['event_name'],
                    'date': 'manual_collection'
                })
            except (ValueError, TypeError):
                continue
    
    print(f"  Added {manual_users_added} unique user-role pairs from manual Discord interests")
    
    # Convert to flat list for CSV output
    print("\nCreating final assignments list...")
    assignments_list = []
    for role_id, users in user_role_assignments.items():
        # Get role name from mappings
        role_info = mappings_df[mappings_df['matched_role_id'] == role_id]
        if len(role_info) > 0:
            role_name = role_info.iloc[0]['matched_role_name']
        else:
            role_name = f"Unknown Role ({role_id})"
        
        for user_id, user_data in users.items():
            # Get source breakdown
            source_counts = {}
            for source in user_data['sources']:
                source_type = source['type']
                source_counts[source_type] = source_counts.get(source_type, 0) + 1
            
            assignments_list.append({
                'role_id': role_id,
                'role_name': role_name,
                'user_id': user_id,
                'username': user_data['username'],
                'total_events': len(user_data['sources']),
                'schedule_bot_events': source_counts.get('schedule_bot', 0),
                'discord_scheduled_events': source_counts.get('discord_scheduled', 0),
                'manual_interest_events': source_counts.get('manual_discord_interest', 0),
                'source_types': ','.join(sorted(set(s['type'] for s in user_data['sources'])))
            })
    
    # Create DataFrame and save
    assignments_df = pd.DataFrame(assignments_list)
    assignments_df = assignments_df.sort_values(['role_name', 'total_events'], ascending=[True, False])
    
    # Save detailed assignments
    assignments_path = os.path.join(OUTPUT_DIR, 'user_role_assignments_FINAL.csv')
    assignments_df.to_csv(assignments_path, index=False)
    
    # Create summary statistics
    print("\n" + "=" * 80)
    print("FINAL ASSIGNMENT SUMMARY:")
    print("=" * 80)
    print(f"Total unique users to be assigned roles: {len(assignments_df['user_id'].unique())}")
    print(f"Total role assignments to be made: {len(assignments_df)}")
    
    # Show breakdown by source type
    print("\nUsers by source type:")
    all_users = set(assignments_df['user_id'].unique())
    
    schedule_bot_users = set(assignments_df[assignments_df['schedule_bot_events'] > 0]['user_id'].unique())
    discord_scheduled_users = set(assignments_df[assignments_df['discord_scheduled_events'] > 0]['user_id'].unique())
    manual_users = set(assignments_df[assignments_df['manual_interest_events'] > 0]['user_id'].unique())
    
    print(f"  - ScheduleBot only: {len(schedule_bot_users - discord_scheduled_users - manual_users)}")
    print(f"  - Discord scheduled only: {len(discord_scheduled_users - schedule_bot_users - manual_users)}")
    print(f"  - Manual interests only: {len(manual_users - schedule_bot_users - discord_scheduled_users)}")
    print(f"  - Multiple sources: {len((schedule_bot_users & discord_scheduled_users) | (schedule_bot_users & manual_users) | (discord_scheduled_users & manual_users))}")
    
    print("\nAssignments per role:")
    print("-" * 50)
    
    role_summary = assignments_df.groupby('role_name').agg({
        'user_id': 'count',
        'total_events': 'sum',
        'schedule_bot_events': 'sum',
        'discord_scheduled_events': 'sum',
        'manual_interest_events': 'sum'
    }).rename(columns={'user_id': 'users'})
    
    # Sort by number of users descending
    role_summary = role_summary.sort_values('users', ascending=False)
    
    for role, data in role_summary.iterrows():
        print(f"{role:25} {int(data['users']):4} users | Events: {int(data['total_events']):4} (SB:{int(data['schedule_bot_events']):3} DS:{int(data['discord_scheduled_events']):3} MI:{int(data['manual_interest_events']):3})")
    
    print(f"\n✅ Final assignments saved to: {assignments_path}")
    print("\nNext step: Review the file and run the role application script!")
    
    return assignments_df

if __name__ == "__main__":
    assignments_df = generate_user_role_assignments_with_manual()