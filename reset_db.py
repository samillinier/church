from app import app, db
import os

# Delete the existing database file
db_file = 'church.db'
if os.path.exists(db_file):
    os.remove(db_file)
    print(f"Deleted existing {db_file}")

# Create all tables
with app.app_context():
    db.create_all()
    print("Created new database with all tables") 