# API Documentation

Base URL: `http://localhost:5000` (Default Flask Port)

## Authentication (User)
- **POST** `/api/register` ลงทะเบียนผู้ป่วยใหม่
- **POST** `/api/login` เข้าสู่ระบบผู้ป่วย

## Authentication (Admin)
- **POST** `/api/admin/login` เข้าสู่ระบบเจ้าหน้าที่ (Admin/Staff)

## Public Data
- **GET** `/api/doctors` ดึงรายชื่อแพทย์ทั้งหมด (รองรับ filter: `?department=`, `?specialist=`)
- **GET** `/api/departments` ดึงรายชื่อแผนกทั้งหมด

## Bookings (User & Operations)
- **POST** `/api/bookings` สร้างการจองใหม่ (Booking)
- **GET** `/api/bookings` ดึงรายการจองทั้งหมด (ใช้สำหรับ History / Admin Dashboard)
- **GET** `/api/bookings/{booking_id}` ดูรายละเอียดการจอง
- **PUT** `/api/bookings/{booking_id}` อัพเดทข้อมูลการจอง (เช่น เลื่อนนัด, เปลี่ยนสถานะ Check-in)
- **DELETE** `/api/bookings/{booking_id}` ยกเลิกหรือลบการจอง

## Admin Management (Staff)
- **GET** `/api/admin/staff` ดึงรายชื่อเจ้าหน้าที่ทั้งหมด
- **POST** `/api/admin/staff` สร้างบัญชีเจ้าหน้าที่ใหม่
- **PUT** `/api/admin/staff/{staff_id}` แก้ไขข้อมูลเจ้าหน้าที่
- **DELETE** `/api/admin/staff/{staff_id}` ลบบัญชีเจ้าหน้าที่

## Admin Management (Doctors)
- **POST** `/api/admin/doctors` เพิ่มรายชื่อแพทย์ใหม่
- **PUT** `/api/admin/doctors/{doctor_id}` แก้ไขข้อมูลแพทย์ (ตารางออกตรวจ, สถานะ)
- **DELETE** `/api/admin/doctors/{doctor_id}` ลบรายชื่อแพทย์

## Notifications
- **GET** `/api/notifications` ดึงรายการแจ้งเตือน (นัดหมายใกล้ถึง, จองสำเร็จ)

-------
 