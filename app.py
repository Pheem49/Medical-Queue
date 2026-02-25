from flask import Flask, render_template, session, redirect, url_for
from models import db, User       # ดึงตัวแปร db และตาราง User มาจาก models.py
from backend import api_bp        # ดึงเส้นทาง API มาจาก backend.py

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['TEMPLATES_AUTO_RELOAD'] = True

#-------- ### -- database configuration and setup -- ### ---------->>>
# ตั้งค่าที่อยู่ฐานข้อมูล
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ผูกตัวแปร db (จาก models) เข้ากับ app ปัจจุบัน
db.init_app(app)

# สั่งให้สร้างไฟล์ฐานข้อมูล my_database.db จริงๆ ขึ้นมา
with app.app_context():
    db.create_all()

# ลงทะเบียน Blueprint ให้แอพรู้จัก API หลังบ้าน
app.register_blueprint(api_bp)

#---------- ### -- Frontend routes -- ### ---------->>>

# หน้า Home
@app.route("/")
def Home():
    return render_template("home.html",title="Home")

# หน้าลงทะเบียนผู้ใช้
@app.route("/register")
def Register():
    if 'user_id' in session:
        return redirect(url_for('Home'))
    return render_template("register.html", title="Register")

# หน้า login ผู้ใช้
@app.route("/login")
def Login():
    if 'user_id' in session:
        return redirect(url_for('Home'))
    return render_template("login.html", title="Login")

# หน้า login Admin
@app.route("/staff/login")
def StaffLogin():
    return render_template("staff_login.html", title="Staff Login")

# หน้าการแจ้งเตือน 
@app.route("/notification")
def Notification():
    return render_template("notification.html", title="Notification")

# หน้าจองคิวตรวจ
@app.route("/booking")
def Booking():
    return render_template("booking.html", title="Booking")

# หน้าดูบัตรคิวของฉัน
@app.route("/mytickets")
def MyTickets():
    return render_template("mytickets.html", title="My Tickets")

# หน้าดูประวัติของฉัน
@app.route("/history")
def History():
    return render_template("history.html", title="History")

# หน้าเงื่อนไขการให้บริการ
@app.route("/terms")
def Terms():
    return render_template("terms.html", title="Terms of Service")

# หน้านโยบายความเป็นส่วนตัว
@app.route("/privacy")
def Privacy():
    return render_template("privacy.html", title="Privacy Policy")

# หน้าสแกน QR Code , ค้นหา Booking ID
@app.route("/staff/checkin")
def StaffCheckin():
    return render_template("staff_checkin.html", title="Staff Check-in")

# หน้าตรวจสอบรายชื่อผู้ป่วยสำหรับ Admin
@app.route("/staff/patients")
def StaffPatients():
    return render_template("staff_patients.html", title="Staff Patients")

# หน้าดูประวัติการจองทั้งหมด สำหรับ Admin
@app.route("/staff/history")
def StaffHistory():
    return render_template("staff_history.html", title="Staff History")

# หน้าจัดการรายชื่อแพทย์
@app.route("/staff/doctors")
def StaffDoctors():
    return render_template("staff_doctors.html", title="Staff Doctors")


if __name__ == "__main__":
    app.run(debug=True)