from app import app, db
from sqlalchemy import text
import traceback

def reset_db():
    with app.app_context():
        try:
            # Drop all tables
            print("Dropping all tables...")
            tables = [
                'user',
                'notification',
                'cell_team',
                'member',
                'document',
                'marriage',
                'appointment',
                'finance_category',
                'finance_transaction',
                'financial_report',
                'budget',
                'teaching_program',
                'teaching_teacher',
                'teaching_student',
                'teaching_material',
                'teaching_event',
                'cell_team_members'
            ]
            
            for table in tables:
                try:
                    print(f"Dropping table: {table}")
                    db.session.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
                except Exception as e:
                    print(f"Error dropping table {table}: {str(e)}")
            
            db.session.commit()
            print("All tables dropped successfully")
            
            # Recreate tables
            print("Recreating tables...")
            db.create_all()
            print("Tables recreated successfully")
            
            return True
        except Exception as e:
            print(f"Error resetting database: {str(e)}")
            print(f"Full error traceback: {traceback.format_exc()}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    reset_db() 