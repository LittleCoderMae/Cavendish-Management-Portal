from app import create_app, db
from app.models import User, Student, Lecturer
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Check if lecturer_id column exists
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('user')]
    
    print("Current columns in user table:", columns)
    
    if 'lecturer_id' not in columns:
        print("Adding lecturer_id column to user table...")
        try:
            # Use db.session.execute() instead of db.engine.execute()
            db.session.execute(text('ALTER TABLE user ADD COLUMN lecturer_id INTEGER REFERENCES lecturer(id)'))
            db.session.commit()
            print("lecturer_id column added successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding lecturer_id: {e}")
    else:
        print("lecturer_id column already exists")
    
    # Also check for other missing columns that your model expects
    missing_columns = []
    expected_columns = ['reset_token', 'reset_token_expiry', 'created_at', 'last_login']
    
    for column in expected_columns:
        if column not in columns:
            missing_columns.append(column)
    
    if missing_columns:
        print(f"Adding missing columns: {missing_columns}")
        
        for column in missing_columns:
            try:
                if column in ['reset_token']:
                    db.session.execute(text(f'ALTER TABLE user ADD COLUMN {column} VARCHAR(128)'))
                elif column == 'reset_token_expiry':
                    db.session.execute(text(f'ALTER TABLE user ADD COLUMN {column} DATETIME'))
                elif column in ['created_at', 'last_login']:
                    db.session.execute(text(f'ALTER TABLE user ADD COLUMN {column} DATETIME'))
                print(f"Added {column} column")
            except Exception as e:
                db.session.rollback()
                print(f"Error adding {column}: {e}")
        
        db.session.commit()
    
    print("Migration completed!")