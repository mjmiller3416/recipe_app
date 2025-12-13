import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database.db import DatabaseSession
from sqlalchemy import text



with DatabaseSession() as session:
    result = session.execute(text("PRAGMA foreign_keys")).scalar()
    print(f"Foreign keys enabled: {result}")
