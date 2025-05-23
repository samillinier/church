from app import app, db
import os

def reset_database():
    with app.app_context():
        # Remove the existing database file
        db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'church.db')
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"Removed existing database: {db_file}")
        
        # Create all tables
        db.create_all()
        print("Created new database with updated schema")

if __name__ == '__main__':
    reset_database() 