#!/usr/bin/env python
"""
Script to create a test lecturer user for testing the lecturer login form.
"""
from app import create_app, db
from app.models import User, Lecturer

def create_test_lecturer():
    """Create a test lecturer account."""
    app = create_app()
    
    with app.app_context():
        # Check if lecturer already exists
        existing_lecturer = User.query.filter_by(email='lecturer@cavendish.edu', role='lecturer').first()
        if existing_lecturer:
            print("✓ Test lecturer already exists!")
            print(f"  Email: {existing_lecturer.email}")
            print(f"  Username: {existing_lecturer.username}")
            return
        
        # Create lecturer profile
        lecturer = Lecturer(
            staff_number='LCT001',
            name='Dr. Elara Vance',
            email='lecturer@cavendish.edu',
            department='Computer Science',
            phone='+260-123-4567'
        )
        
        db.session.add(lecturer)
        db.session.flush()  # Get the lecturer ID
        
        # Create user account linked to lecturer
        user = User(
            username='elara_vance',
            email='lecturer@cavendish.edu',
            role='lecturer',
            lecturer_id=lecturer.id
        )
        user.set_password('SecurePass123')  # Set password
        
        db.session.add(user)
        db.session.commit()
        
        print("✓ Test lecturer account created successfully!")
        print("\nTest Lecturer Credentials:")
        print("  Email: lecturer@cavendish.edu")
        print("  Password: SecurePass123")
        print("  Name: Dr. Elara Vance")
        print("  Staff Number: LCT001")
        print("  Department: Computer Science")
        print("\nYou can now log in at: http://127.0.0.1:5000/lecturer/login")

if __name__ == '__main__':
    create_test_lecturer()
