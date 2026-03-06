from app import app, db
from models import Department

def seed_departments():
    departments = [
        "Cardiology",
        "Neurology",
        "Orthopedics",
        "Pediatrics"
    ]

    with app.app_context():
        # Check if they already exist to avoid duplicates
        existing_dept_names = [d.name for d in Department.query.all()]
        
        for name in departments:
            if name not in existing_dept_names:
                new_dept = Department(name=name)
                db.session.add(new_dept)
                print(f"Added department: {name}")
            else:
                print(f"Department already exists: {name}")
        
        db.session.commit()
        print("Department seeding completed successfully.")

if __name__ == "__main__":
    seed_departments()
