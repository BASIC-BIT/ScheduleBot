import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import from the notebook
exec(open('role_migration_pipeline.ipynb').read())

# Run the async function
asyncio.run(fetch_all_discord_roles())