# QUICK REFERENCE - ROLE MIGRATION

## What This Is
Automated system to assign Discord roles based on historical ScheduleBot attendance

## The Golden File
`user_role_assignments_FINAL_FIXED_20250802_232315.csv` - This is what we applied

## To Run Again
```bash
python apply_roles_with_proper_rate_limit.py production-apply
```

## Key Stats
- 396 roles applied to 150 users
- 21 different class/event roles
- Took 12 minutes with rate limiting

## Most Important Issue
**ALWAYS** load CSV files with `dtype={'role_id': str, 'user_id': str}` or role IDs will be corrupted!

## What Changed
- Removed: Community Manager role
- Changed: DJ → DJ Class  
- Removed: CHILL, Wotagei, Pole Dancing, Portal Posse, VR Fundamentals (didn't exist)

## Bot Needs
1. "Manage Roles" permission
2. Role higher than any role it assigns
3. Currently uses "RoleBot" role

## If Something Breaks
1. Check `PROJECT_SUMMARY_ROLE_MIGRATION.md` for full details
2. Run `python check_bot_permissions.py` to debug
3. Discord rate limit = wait 1 sec between role adds

## Data Sources Combined
1. ScheduleBot database (539 events)
2. Discord scheduled events (limited)
3. Manual interest collection (160 entries)

Created: August 2, 2025