# API Documentation

Base URL: `http://localhost:5000` (Default Flask Port)

## User (Patient)

### Authentication
- **POST** `/api/register` ลงทะเบียนผู้ป่วยใหม่ 
- **POST** `/api/login` เข้าสู่ระบบผู้ป่วย 

### Browsing & Information
- **GET** `/api/doctors` ดึงรายชื่อแพทย์ทั้งหมด (รองรับ filter: `?department=`, `?specialist=`) 
- **GET** `/api/departments` ดึงรายชื่อแผนกทั้งหมด 

### My Bookings
- **POST** `/api/bookings` สร้างการจองใหม่ (Booking) 
- **GET** `/api/bookings` ดึงประวัติการจองของฉัน (My Booking History) 
- **GET** `/api/bookings/{booking_id}` ดูรายละเอียดการจอง 
- **PUT** `/api/bookings/{booking_id}` อัพเดทข้อมูลการจอง (เช่น เลื่อนนัด - Reschedule)4
- **DELETE** `/api/bookings/{booking_id}` ยกเลิกการจอง 

### Notifications
- **GET** `/api/notifications` ดึงรายการแจ้งเตือน (นัดหมายใกล้ถึง, จองสำเร็จ) 

---

## Admin (Staff)

### Authentication
- **POST** `/api/admin/login` เข้าสู่ระบบเจ้าหน้าที่ (Admin/Staff) 

### Operations & Dashboard (แฟรงค์ - นายรัชชานนท์)
- **GET** `/api/admin/bookings` ดึงรายการจองทั้งหมด (Admin Dashboard / All History)
- **POST** `/api/admin/bookings/{booking_id}` อัพเดทสถานะการจอง (เช่น Check-in, Completed)

### Doctor Management (ภีม - นายอภิสิทธิ์)
- **GET** `/api/doctors` ดึงรายชื่อแพทย์ทั้งหมด
- **POST** `/api/admin/doctors` เพิ่มรายชื่อแพทย์ใหม่
- **PUT** `/api/admin/doctors/{doctor_id}` แก้ไขข้อมูลแพทย์
- **DELETE** `/api/admin/doctors/{doctor_id}` ลบรายชื่อแพทย์

### Slot management (ภีม - นายอภิสิทธิ์)
- **GET** `/api/admin/slots` ดึง slot ทั้งหมดไปโชว์
- **POST** `/api/admin/slots` เพิ่ม slot ใหม่
- **PUT** `/api/admin/slots/{slot_id}` แก้ไขข้อมูล slot (เวลา, จำนวน)
--