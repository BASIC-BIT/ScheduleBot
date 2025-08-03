import os
import pandas as pd
from datetime import datetime

def generate_user_role_assignments_with_manual(schedule_events_df, discord_events_df, mappings_df=None, output_dir='outputs'):
    """
    Generate user-to-role assignments based on historical attendance data,
    Discord event subscribers, and manually collected Discord interests.
    """
    # Load the reviewed mappings if not provided
    if mappings_df is None:
        mappings_path = os.path.join(output_dir, 'event_role_mappings_reviewed.csv')
        if os.path.exists(mappings_path):
            print("Loading reviewed mappings...")
            mappings_df = pd.read_csv(mappings_path)
        else:
            mappings_path = os.path.join(output_dir, 'event_role_mappings_for_review.csv')
            print("Loading automatic mappings (no reviewed file found)...")
            mappings_df = pd.read_csv(mappings_path)
    
    # Load manual Discord interests with user IDs
    manual_interests_path = os.path.join(output_dir, 'manual_discord_interests_with_ids.csv')
    manual_interests_df = None
    if os.path.exists(manual_interests_path):
        print("Loading manual Discord interests...")
        manual_interests_df = pd.read_csv(manual_interests_path)
        print(f"  Loaded {len(manual_interests_df)} manual interest records")
    
    # Dictionary to store user-role assignments
    # Format: {role_id: {user_id: {'username': name, 'sources': [list of events]}}}
    user_role_assignments = {}
    
    print("\nProcessing Schedule Bot attendance data...")
    print("=" * 80)
    
    # Process schedule bot events
    if schedule_events_df is not None:
        events_processed = 0
        attendees_processed = 0
        
        for _, event in schedule_events_df.iterrows():
            event_title = event['EventTitle']
            
            # Find the role mapping for this event
            mapping = mappings_df[
                (mappings_df['event_source'] == 'schedule_bot') & 
                (mappings_df['event_title'] == event_title)
            ]
            
            if len(mapping) == 0 or pd.isna(mapping.iloc[0]['matched_role_id']):
                continue
            
            events_processed += 1
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
                        
                        user_role_assignments[role_id][user_id]['sources'].append({
                            'type': 'schedule_bot',
                            'event': event_title,
                            'date': str(event['StartTime'])
                        })
                        attendees_processed += 1
                    except (ValueError, IndexError):
                        continue
        
        print(f"Processed {events_processed} schedule bot events with {attendees_processed} attendances")
    
    print("\nProcessing Discord scheduled event subscribers...")
    print("=" * 80)
    
    # Process Discord scheduled events
    if discord_events_df is not None and len(discord_events_df) > 0:
        events_processed = 0
        subscribers_processed = 0
        
        for _, event in discord_events_df.iterrows():
            event_name = event['event_name']
            
            # Find the role mapping for this event
            mapping = mappings_df[
                (mappings_df['event_source'] == 'discord_scheduled') & 
                (mappings_df['event_title'] == event_name)
            ]
            
            if len(mapping) == 0 or pd.isna(mapping.iloc[0]['matched_role_id']):
                continue
            
            events_processed += 1
            role_id = int(mapping.iloc[0]['matched_role_id'])
            role_name = mapping.iloc[0]['matched_role_name']
            
            # Initialize role dict if needed
            if role_id not in user_role_assignments:
                user_role_assignments[role_id] = {}
            
            # Process subscribers
            if pd.notna(event.get('subscriber_ids')) and event.get('subscriber_ids') != '[]':
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
                            
                            user_role_assignments[role_id][user_id]['sources'].append({
                                'type': 'discord_scheduled',
                                'event': event_name,
                                'date': str(event['start_time'])
                            })
                            subscribers_processed += 1
                        except ValueError:
                            continue
                except:
                    continue
        
        print(f"Processed {events_processed} Discord events with {subscribers_processed} subscribers")
    
    print("\nProcessing Manual Discord Interests...")
    print("=" * 80)
    
    # Process manual Discord interests
    if manual_interests_df is not None:
        manual_users_added = 0
        manual_sources_added = 0
        
        for _, interest in manual_interests_df.iterrows():
            if pd.notna(interest['user_id']) and pd.notna(interest['role_id']):
                try:
                    user_id = int(float(interest['user_id']))  # Handle scientific notation
                    role_id = int(float(interest['role_id']))
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
                    manual_sources_added += 1
                except (ValueError, TypeError) as e:
                    continue
        
        print(f"Added {manual_users_added} new users from manual Discord interests")
        print(f"Added {manual_sources_added} manual interest sources")
    
    # Convert to flat list for CSV output
    assignments_list = []
    for role_id, users in user_role_assignments.items():
        # Get role name from mappings
        role_info = mappings_df[mappings_df['matched_role_id'] == role_id]
        if len(role_info) > 0:
            role_name = role_info.iloc[0]['matched_role_name']
        else:
            role_name = f"Unknown Role ({role_id})"
        
        for user_id, user_data in users.items():
            assignments_list.append({
                'role_id': str(role_id),  # Convert to string to preserve full ID
                'role_name': role_name,
                'user_id': str(user_id),  # Convert to string to preserve full ID
                'username': user_data['username'],
                'event_count': len(user_data['sources']),
                'first_event': min(s['date'] for s in user_data['sources']),
                'last_event': max(s['date'] for s in user_data['sources']),
                'source_types': ','.join(sorted(set(s['type'] for s in user_data['sources'])))
            })
    
    # Create DataFrame and save
    assignments_df = pd.DataFrame(assignments_list)
    assignments_df = assignments_df.sort_values(['role_name', 'event_count'], ascending=[True, False])
    
    # Save detailed assignments
    assignments_path = os.path.join(output_dir, 'user_role_assignments_combined_for_review.csv')
    assignments_df.to_csv(assignments_path, index=False)
    
    # Create summary statistics
    print("\nAssignment Summary:")
    print("=" * 80)
    print(f"Total unique users to be assigned roles: {len(assignments_df['user_id'].unique())}")
    print(f"Total role assignments to be made: {len(assignments_df)}")
    
    # Show breakdown by source type
    print("\nUsers by source type:")
    for source_type in ['schedule_bot', 'discord_scheduled', 'manual_discord_interest']:
        users_with_source = assignments_df[assignments_df['source_types'].str.contains(source_type)]
        print(f"  - {source_type}: {len(users_with_source['user_id'].unique())} unique users")
    
    print("\nAssignments per role:")
    
    role_summary = assignments_df.groupby('role_name').agg({
        'user_id': 'count',
        'event_count': 'sum'
    }).rename(columns={'user_id': 'users', 'event_count': 'total_events'})
    
    print(role_summary.to_string())
    
    print(f"\nDetailed assignments saved to: {assignments_path}")
    print("\nPlease review the assignments file before proceeding to the final step.")
    
    return assignments_df


if __name__ == "__main__":
    # Load the data files
    print("Loading data files...")
    
    try:
        schedule_events_df = pd.read_csv('outputs/schedule_bot_events.csv')
        print(f"Loaded {len(schedule_events_df)} schedule bot events")
    except:
        print("Could not load schedule bot events")
        schedule_events_df = None
    
    try:
        discord_events_df = pd.read_csv('outputs/discord_scheduled_events.csv')
        print(f"Loaded {len(discord_events_df)} Discord scheduled events")
    except:
        print("Could not load Discord scheduled events")
        discord_events_df = None
    
    # Generate the assignments
    assignments_df = generate_user_role_assignments_with_manual(
        schedule_events_df, 
        discord_events_df
    )