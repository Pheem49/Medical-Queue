#Api Documentation

##Authentication
- Post /api/auth/register สมัครสมาชิก
- Post /api/auth/login ล็อกอิน
- Post /api/admin/login ล็อกอิน admin

##apatments
- Get /api/apatment ดึงแผนกทั้งหมด

##Doctor
- get /api/doctor ดึงรายชื่อ doctor ทั้งหมด
- post /api/doctor เพิ่มรายชื่อ doctor
- get /api/doctor/{id} ดึงรายละเอียดหมอรายบุคคล
- Delete /api/doctor/{id} ลบรายชื่อหมอ

##User
- get /api/user ดึงรายชื่อ user ทั้งหมด

##booking
- Get /api/admin/booking/history ดึงประวัติการจอง
- Get /api/booking/booker ดึงรายชื่อคนจอง
- Get /api/booking/{Token_id} ดึงข้อมูล Qr code 
- post /api/booking/{Booking_id} ส่งข้อมูล Booking_id
- Get /api/booking/{Booking_id} ดึงข้อมูล Booking_id
- post /api/booking/{Token_id} ส่งข้อมูล Qr code 
- 