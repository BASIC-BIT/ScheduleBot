import pandas as pd
import os
from difflib import SequenceMatcher

def similarity(a, b):
    """Calculate string similarity between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def map_usernames_to_ids():
    """
    Map the manually collected usernames to Discord user IDs.
    """
    # Load the manual interests data
    manual_interests = pd.read_csv('outputs/manual_discord_interests_structured.csv')
    
    # Load the username lookup table
    try:
        lookup_df = pd.read_csv('outputs/faceless_username_lookup.csv')
    except FileNotFoundError:
        print("ERROR: faceless_username_lookup.csv not found!")
        print("Please run fetch_all_discord_members.py first to generate the member list.")
        return
    
    # Create a mapping for each unique username in manual interests
    unique_usernames = manual_interests['username'].unique()
    
    mappings = []
    unmapped = []
    
    print(f"Attempting to map {len(unique_usernames)} unique usernames to Discord IDs...")
    print("=" * 70)
    
    for username in unique_usernames:
        # Skip deleted users
        if 'deleted_user' in username.lower():
            unmapped.append({
                'username': username,
                'reason': 'Deleted user account'
            })
            continue
        
        # First try exact match (case-insensitive)
        exact_matches = lookup_df[lookup_df['lookup_name'] == username.lower()]
        
        if len(exact_matches) > 0:
            # If multiple matches, just take the first one
            # (we can add bot filtering later if the column exists)
            match = exact_matches.iloc[0]
            
            mappings.append({
                'manual_username': username,
                'matched_user_id': match['user_id'],
                'matched_username': match.get('username', match.get('original_name', username)),
                'match_type': 'exact',
                'confidence': 1.0
            })
        else:
            # Try fuzzy matching
            best_match = None
            best_score = 0
            
            for _, row in lookup_df.iterrows():
                score = similarity(username, row['original_name'])
                if score > best_score and score > 0.85:  # 85% similarity threshold
                    best_score = score
                    best_match = row
            
            if best_match is not None:
                mappings.append({
                    'manual_username': username,
                    'matched_user_id': best_match['user_id'],
                    'matched_username': best_match.get('username', best_match.get('original_name', username)),
                    'match_type': 'fuzzy',
                    'confidence': best_score
                })
            else:
                unmapped.append({
                    'username': username,
                    'reason': 'No match found'
                })
    
    # Convert to DataFrames
    mappings_df = pd.DataFrame(mappings)
    unmapped_df = pd.DataFrame(unmapped)
    
    # Save the mappings
    mappings_df.to_csv('outputs/manual_username_to_id_mappings.csv', index=False)
    unmapped_df.to_csv('outputs/manual_username_unmapped.csv', index=False)
    
    # Print summary
    print(f"\nMapping Results:")
    print(f"  Successfully mapped: {len(mappings_df)}")
    print(f"  - Exact matches: {len(mappings_df[mappings_df['match_type'] == 'exact'])}")
    print(f"  - Fuzzy matches: {len(mappings_df[mappings_df['match_type'] == 'fuzzy'])}")
    print(f"  Unmapped: {len(unmapped_df)}")
    
    if len(unmapped_df) > 0:
        print(f"\nUnmapped usernames:")
        for _, row in unmapped_df.iterrows():
            try:
                print(f"  - {row['username']} ({row['reason']})")
            except UnicodeEncodeError:
                print(f"  - [Unicode username] ({row['reason']})")
    
    # Now merge the user IDs back into the manual interests data
    if len(mappings_df) > 0:
        # Create the final manual interests with user IDs
        manual_with_ids = manual_interests.merge(
            mappings_df[['manual_username', 'matched_user_id']],
            left_on='username',
            right_on='manual_username',
            how='left'
        )
        
        # Rename and clean up columns
        manual_with_ids['user_id'] = manual_with_ids['matched_user_id']
        manual_with_ids = manual_with_ids.drop(['manual_username', 'matched_user_id'], axis=1)
        
        # Save the final data with user IDs
        output_path = 'outputs/manual_discord_interests_with_ids.csv'
        manual_with_ids.to_csv(output_path, index=False)
        print(f"\nSaved manual interests with user IDs to: {output_path}")
        
        # Create summary by role
        role_summary = manual_with_ids[manual_with_ids['user_id'].notna()].groupby('role_name')['user_id'].nunique().reset_index(name='unique_users_with_ids')
        print(f"\nUsers with IDs by role:")
        for _, row in role_summary.iterrows():
            print(f"  - {row['role_name']}: {row['unique_users_with_ids']} users")

if __name__ == "__main__":
    map_usernames_to_ids()