import sqlite3  # Imports

# Connect to the database
db_path = "app/database/app_data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Query schema_version
cursor.execute("SELECT * FROM schema_version;")
rows = cursor.fetchall()

# Print results
for row in rows:
    print(row)

conn.close()
