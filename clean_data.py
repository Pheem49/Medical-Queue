from app import app, db
from models import User, Admin, Department, Doctor, DoctorToDepartment, AppointmentSlot, Booking

def clean_seeded_data():
    with app.app_context():
        print("Starting data cleanup (preserving User and Admin)...")
        
        try:
            # 1. ลบการจอง (Booking)
            print("Deleting Bookings...")
            db.session.query(Booking).delete()
            
            # 2. ลบ Slot เวลานัด (AppointmentSlot)
            print("Deleting Appointment Slots...")
            db.session.query(AppointmentSlot).delete()
            
            # 3. ลบความสัมพันธ์แพทย์กับแผนก (DoctorToDepartment)
            print("Deleting Doctor to Department links...")
            db.session.query(DoctorToDepartment).delete()
            
            # 4. ลบข้อมูลแพทย์ (Doctor)
            print("Deleting Doctors...")
            db.session.query(Doctor).delete()
            
            # 5. ลบข้อมูลแผนก (Department)
            print("Deleting Departments...")
            db.session.query(Department).delete()
            
            # ทำการ Commit การลบทั้งหมด
            db.session.commit()
            print("\nCleanup successfully completed!")
            print("Preserved: User and Admin tables.")
            
        except Exception as e:
            db.session.rollback()
            print(f"\nAn error occurred during cleanup: {e}")
            print("Rollback performed.")

if __name__ == "__main__":
    clean_seeded_data()
