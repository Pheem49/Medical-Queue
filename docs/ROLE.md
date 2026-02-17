# Frontend Documentation



## สมาชิกในทีมและการแบ่งงาน (Team Members & Route Assignments)
1. นางสาวกฤติมา ทองมวล
Role: Login, Register 
Authentication
- `index.html`: **Login Page** - หน้าเข้าสู่ระบบสำหรับผู้ป่วย
- `register.html`: **Registration Page** - หน้าลงทะเบียนผู้ป่วยใหม่

2. นายจิรัฐิติกาล ลาเลิศ
Role: Booking(เลือกแผนก/แพทย์), confirm
- `booking.html`: **Select Logic** - หน้าเลือกแพทย์หรือแผนก
- `confirm.html`: **Confirm Booking** - หน้าตรวจสอบและยืนยันข้อมูลการจอง

3. นายธีรัช มิฉะนั้น
Role: home, datetime
- `home.html`: **Main Dashboard** - หน้าหลักแสดงเมนูและข้อมูลเบื้องต้น
- `datetime.html`: **Select Schedule** - หน้าเลือกวันและเวลาที่ต้องการจอง

4. นายทีปกรณ์ แก่นกุล 
Role: datetime, details
- `datetime.html`: **Select Schedule** - หน้าเลือกวันและเวลาที่ต้องการจอง
- `details.html`: **Booking Details** - หน้าดูรายละเอียดการจองแต่ละรายการ

5. นายวุฒิภัทร วิริยเสนกุล
Role: history, notification
- `history.html`: **Booking History** - หน้าดูประวัติการจองทั้งหมด
- `notification.html`: **Notification Center** - หน้าดูรายการแจ้งเตือนต่างๆ

6. นายพงศกร กอคูณ
Role: QR Code scan, canel Booking
- `myticket.html`: **Booking Success** - หน้าแสดงตั๋ว/QR Code เมื่อจองสำเร็จ
- `details.html`: **Booking Details** - หน้าดูรายละเอียดการจองแต่ละรายการ

7. นายรัชชานนท์ อรรถพันธ์
Role: admin(ตรวจสอบรายชื่อ), admin(ดูประวัติการจอง)
- `admin.html`: **Unified Admin Dashboard** - หน้าจัดการรวมสำหรับเจ้าหน้าที่:
    - ดูรายการจองทั้งหมด (All Bookings)
    - ตรวจสอบรายชื่อการจอง (Check Booking List)

8. นายอภิสิทธิ์ พรหมมา
Role: admin(home), admin(จัดการรายชื่อแพทย์)
- `admin.html`: **Unified Admin Dashboard** - หน้าจัดการรวมสำหรับเจ้าหน้าที่:
    - หน้าหลักadmin (Admin Home)
    - จัดการรายชื่อแพทย์ (Manage Doctors)



## User (Patient) - Frontend Pages

### Authentication
- `index.html`: **Login Page** - หน้าเข้าสู่ระบบสำหรับผู้ป่วย
- `register.html`: **Registration Page** - หน้าลงทะเบียนผู้ป่วยใหม่

### Dashboard & Main
- `home.html`: **Main Dashboard** - หน้าหลักแสดงเมนูและข้อมูลเบื้องต้น

### Booking Process (Flow)
1. `booking.html`: **Select Logic** - หน้าเลือกแพทย์หรือแผนก
2. `datetime.html`: **Select Schedule** - หน้าเลือกวันและเวลาที่ต้องการจอง
3. `confirm.html`: **Confirm Booking** - หน้าตรวจสอบและยืนยันข้อมูลการจอง
4. `myticket.html`: **Booking Success** - หน้าแสดงตั๋ว/QR Code เมื่อจองสำเร็จ

### History & Management
- `history.html`: **Booking History** - หน้าดูประวัติการจองทั้งหมด
- `details.html`: **Booking Details** - หน้าดูรายละเอียดการจองแต่ละรายการ

### Notifications
- `notification.html`: **Notification Center** - หน้าดูรายการแจ้งเตือนต่างๆ

---

## Admin (Staff) - Frontend Pages

### Dashboard & Management
- `admin.html`: **Unified Admin Dashboard** - หน้าจัดการรวมสำหรับเจ้าหน้าที่:
    - ดูรายการจองทั้งหมด (All Bookings)
    - จัดการรายชื่อแพทย์ (Manage Doctors)
    - จัดการเจ้าหน้าที่ (Manage Staff)
