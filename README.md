# Medical Queue Management System

ระบบจัดการคิวโรงพยาบาล แบ่งการทำงานตามฐานข้อมูล 8 ส่วนหลัก

---

## 🛠 คู่มือการติดตั้งและใช้งาน (Getting Started)

### 1. การเตรียมสภาพแวดล้อม (Environment Setup)
แนะนำให้ใช้งานผ่าน Virtual Environment เพื่อแยก Library ของโปรเจกต์ออกจากเครื่องหลัก:
```bash
# สร้าง venv
python -m venv venv

# เปิดใช้งาน (Windows)
.\venv\Scripts\activate

# เปิดใช้งาน (Mac/Linux)
source venv/bin/activate
```

### 2. การติดตั้ง Library
เมื่อเปิดใช้งาน venv เรียบร้อยแล้ว ให้ติดตั้งสิ่งที่จำเป็นผ่าน `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 3. การเตรียมฐานข้อมูล (Database Setup)
ก่อนเริ่มใช้งานครั้งแรก คุณต้องสร้างฐานข้อมูลและเตรียมข้อมูลตัวอย่าง (Admin, แผนก, หมอ) ผ่านไฟล์ Seed:
```bash
python seed.py
```

### 4. การเริ่มใช้งานระบบ (Running the App)
รันคำสั่งเพื่อเปิดเซิร์ฟเวอร์ Flask:
```bash
python app.py
```
จากนั้นเปิด Browser ไปที่: `http://127.0.0.1:5000`

---

## 🏗 แผนการแบ่งงานตามฐานข้อมูลสำหรับ 8 คน (Database-Driven Architecture)

หลังจากตรวจสอบ [models.py](file:///c:/My%20document%20etc/Medical/Medical-Queue/models.py) พบว่าโครงสร้างข้อมูลมีทั้งหมด **8 ตารางหลักพอดีเป๊ะ!** ซึ่งนี่เป็นความลงตัวที่สมบูรณ์แบบมากครับ เราสามารถจับคู่ **1 คน = 1 ตารางฐานข้อมูล (Model)** ไปเลย วิธีนี้นอกจากงานจะแฟร์แล้ว ทุกคนยังได้เรียนรู้การดึงข้อมูล (Query) จากตารางของตัวเองได้อย่างลึกซึ้งด้วยครับ

---

## 8 ตาราง 8 หน้าที่

### 🧑‍💻 คนที่ 1 แป้ง : ตาราง [User](file:///c:/My%20document%20etc/Medical/Medical-Queue/models.py#10-40) (จัดการคนไข้)
**รับผิดชอบ:** ข้อมูลผู้สมัคร / ผู้ป่วยทั่วไปทั้งหมด 
**ไฟล์หน้าบ้าน (Route):** `views/user_routes.py`
**ไฟล์หลังบ้าน (Service):** `services/user_service.py`
- `GET /login` (หน้าเข้าสู่ระบบ)
- `GET /register` (หน้าลงทะเบียน)
- `GET /notification` (หน้าแจ้งเตือน/Feed ข้อมูล)
- `GET /terms` / `GET /privacy` (หน้าเงื่อนไขและนโยบาย)
- `POST /api/register` (ลงทะเบียนสมาชิกใหม่)
- `POST /api/login` (เข้าสู่ระบบ)
- `PUT /api/user/profile` (แก้ไขข้อมูลส่วนตัว)
- **จุดพรีเซนต์:** ระบบสมัครสมาชิก/ล็อกอิน และการจัดการ Session ของคนไข้

### 🧑‍💻 คนที่ 2 คิม : ตาราง [Admin](file:///c:/My%20document%20etc/Medical/Medical-Queue/models.py#42-53) (จัดการเจ้าหน้าที่)
**รับผิดชอบ:** ข้อมูลสิทธิ์การเป็นแอดมินหรือพยาบาล
**ไฟล์หน้าบ้าน (Route):** `views/admin_auth_routes.py`
**ไฟล์หลังบ้าน (Service):** `services/admin_auth_service.py`
- `GET /staff/login` (หน้า Login เจ้าหน้าที่)
- `POST /api/admin/login` (เข้าสู่ระบบเจ้าหน้าที่)
- `GET/POST/DELETE /api/logout` (ออกจากระบบ / เคลียร์ Session)
- **จุดพรีเซนต์:** ระบบความปลอดภัยของเจ้าหน้าที่ และการแยกสิทธิ์ระหว่าง User และ Admin

### 🧑‍💻 คนที่ 3 ซันเดย์: ตาราง [Department](file:///c:/My%20document%20etc/Medical/Medical-Queue/models.py#55-67) (จัดการแผนกการเปิดบริการ)
**รับผิดชอบ:** ลิสต์รายชื่อแผนก และหมวดหมู่การรักษา
**ไฟล์หน้าบ้าน (Route):** `views/department_routes.py`
**ไฟล์หลังบ้าน (Service):** `services/department_service.py`
- `GET /` (หน้า Home ของระบบ)
- `GET /api/departments` (ดึงรายชื่อแผนกทั้งหมด)
- `POST /api/admin/departments` (แอดมินเพิ่มแผนกใหม่)
- `PUT /api/admin/departments/<int:department_id>` (แก้ไขชื่อแผนก)

### 🧑‍💻 คนที่ 4 แฟรงค์: ตาราง [Doctor](file:///c:/My%20document%20etc/Medical/Medical-Queue/models.py#69-99) (จัดการประวัติคุณหมอ)
**รับผิดชอบ:** ฐานข้อมูลแพทย์รายบุคคล (เพิ่ม/ลบแพทย์)
**ไฟล์หน้าบ้าน (Route):** `views/doctor_routes.py`
**ไฟล์หลังบ้าน (Service):** `services/doctor_service.py`
- `GET /staff/doctors` (หน้าจัดการข้อมูลแพทย์สำหรับเจ้าหน้าที่)
- `GET /api/doctors` (ดึงรายชื่อหมอที่พร้อมบริการ)
- `GET /api/admin/doctors` (ดึงรายชื่อหมอทั้งหมดสำหรับแอดมิน)
- `POST /api/admin/doctors` (เพิ่มแพทย์ใหม่)
- `PUT /api/admin/doctors/<int:doctor_id>` (แก้ไขข้อมูลแพทย์)
- `DELETE /api/admin/doctors/<int:doctor_id>` (ลบข้อมูลแพทย์)
- **จุดพรีเซนต์:** การเก็บข้อมูลตารางเวลาแบบ JSON เพื่อความยืดหยุ่น

### 🧑‍💻 คนที่ 5 ภีม : ตาราง [DoctorToDepartment](file:///c:/My%20document%20etc/Medical/Medical-Queue/models.py#101-113) (จัดการความเชี่ยวชาญ / การลิงค์แผนก)
**รับผิดชอบ:** ตารางเชื่อมโยง Many-to-Many ว่าคุณหมอคนไหนอยู่แผนกอะไร
**ไฟล์หน้าบ้าน (Route):** `views/doctor_department_routes.py`
**ไฟล์หลังบ้าน (Service):** `services/doctor_department_service.py`
- `GET /api/department/<int:department_id>/doctors` (ดึงหมอในแผนก)
- `GET /api/doctor/<int:doctor_id>/departments` (ดึงแผนกที่หมอสังกัด)
- `POST /api/admin/assign_doctor` ( Assign หมอเข้าแผนก)
- `DELETE /api/admin/remove_doctor_dept` (ปลดหมอออกจากแผนก)
- **จุดพรีเซนต์:** การจัดการความสัมพันธ์แบบ Many-to-Many ในฐานข้อมูล

### 🧑‍💻 คนที่ 6 ฟีม : ตาราง [AppointmentSlot](file:///c:/My%20document%20etc/Medical/Medical-Queue/models.py#115-164) (ตารางเวลาการเปิดเปิดคิว)
**รับผิดชอบ:** เวลาแต่ละสล็อตที่เปิดรับคนไข้ และระบบ Scanner
**ไฟล์หน้าบ้าน (Route):** `views/slot_routes.py`
**ไฟล์หลังบ้าน (Service):** `services/slot_service.py`
- `GET /staff/checkin` (หน้า Scanner สำหรับเจ้าหน้าที่)
- `GET /api/admin/slots` (ดึงสล็อตเวลาตามหมอ/วันที่)
- `POST /api/admin/slots` (สร้างสล็อตเวลาใหม่)
- `PUT /api/admin/slots/<int:slot_id>/status` (อัปเดตสถานะสล็อต)
- `DELETE /api/admin/slots/<int:slot_id>` (ลบสล็อตเวลา)
- `POST /api/scan/decrypt` (API สำหรับถอดรหัส QR Code)
- **จุดพรีเซนต์:** ระบบ Scanner และการจัดการสล็อตเวลาแบบ Real-time

### 🧑‍💻 คนที่ 7 ปอนด์ : ตาราง [Booking](file:///c:/My%20document%20etc/Medical/Medical-Queue/models.py#166-210) ฝั่งคนไข้ (Create & Read Booking)
**รับผิดชอบ:** กระบวนการจองของคนไข้ และการดูคิวของตนเอง
**ไฟล์หน้าบ้าน (Route):** `views/booking_routes.py`
**ไฟล์หลังบ้าน (Service):** `services/booking_service.py`
- `GET /booking` (หน้าเลือกวัน/เวลาจอง)
- `GET /booking/confirm` (หน้ายืนยันข้อมูลการจอง)
- `GET /mytickets` (หน้าบัตรคิวของฉัน)
- `GET /history` (หน้าประวัติการจอง)
- `POST /api/bookings` (บันทึกข้อมูลการจองใหม่)
- `PUT /api/booking/<int:booking_id>/reschedule` (เลื่อนนัดหมาย)
- `GET /api/booking/<int:booking_id>` (ดูรายละเอียดการจอง)
- `POST /api/booking/<int:booking_id>/cancel` (ยกเลิกการจอง)
- `GET /api/history` (ดึงประวัติการจองทั้งหมดของ User)
- `GET /api/doctor/<int:doctor_id>/available-dates` (ดึงวันที่หมอมีคิวว่าง)
- **จุดพรีเซนต์:** ระบบการจองคิวพร้อมการสร้าง QR Code และการเช็คเงื่อนไขจองซ้อน

### 🧑‍💻 คนที่ 8 บอล : ตาราง [Booking](file:///c:/My%20document%20etc/Medical/Medical-Queue/models.py#166-210) ฝั่งแอดมิน (Booking Management)
**รับผิดชอบ:** การจัดการคิวทั้งหมดของโรงพยาบาล และการอัปเดตสถานะคิว
**ไฟล์หน้าบ้าน (Route):** `views/booking_management_routes.py`
**ไฟล์หลังบ้าน (Service):** `services/booking_management_service.py`
- `GET /staff/patients` (หน้า Dashboard ดูคนไข้วันนี้)
- `GET /staff/history` (หน้าดูประวัติคิวรวมทั้งโรงพยาบาล)
- `GET /api/admin/bookings` (ดึงข้อมูลการจองทั้งหมด)
- `GET /api/admin/bookings/<int:booking_id>` (ดึงข้อมูลการจองสำหรับ Scanner)
- `PUT /api/admin/bookings/<int:booking_id>/status` (อัปเดตสถานะคนไข้ เช่น มารับบริการแล้ว)
- `DELETE /api/bookings/<int:booking_id>` (ลบ/ยกเลิกการจองโดยแอดมิน)
- `GET /api/admin/history` (ดึงประวัติการจองทั้งหมดสำหรับแอดมิน)
- **จุดพรีเซนต์:** ระบบ Dashboard สำหรับเจ้าหน้าที่ และการอัปเดตตัวเลขคิวควบคู่ไปกับสถานะ

---

### บทสรุป 
จับคู่แบบนี้ **ยุติธรรมขั้นสุดยอดครับ** เพราะแบ่งจาก Database 8 ตารางเป๊ะๆ ทุกคนจะได้เขียนโค้ด CRUD (Create, Read, Update, Delete) ครบทุกมิติของตารางตัวเอง โดยมีจุดขายเชิงเทคนิคไปนำเสนออาจารย์แตกต่างกันไปด้วยครับ!

---

### 📊 สรุปจำนวนเส้นทาง (Route Statistics)

จากการวิเคราะห์ไฟล์ในโฟลเดอร์ `views/` ทั้งหมด 8 ไฟล์ พบว่ามีเส้นทางรวมทั้งสิ้น **48 Routes** แบ่งได้ดังนี้:

| ประเภทเส้นทาง | จำนวน | รายละเอียด |
| :--- | :---: | :--- |
| **Frontend Routes** | 15 | หน้า UI สำหรับคนไข้และเจ้าหน้าที่ (HTML Rendering) |
| **API Routes** | 33 | ส่วนเชื่อมต่อข้อมูลหลังบ้าน (JSON API) |
| **รวมทั้งหมด** | **48** | |

---

### 👥 สรุปแยกตามผู้รับผิดชอบ (By Component)

| ลำดับ | รายการตาราง / ผู้รับผิดชอบ | Frontend | API | รวม |
| :---: | :--- | :---: | :---: | :---: |
| 1 | **User** (จัดการคนไข้) | 5 | 3 | 8 |
| 2 | **Admin** (จัดการเจ้าหน้าที่) | 1 | 2 | 3 |
| 3 | **Department** (จัดการแผนก) | 1 | 3 | 4 |
| 4 | **Doctor** (ข้อมูลแพทย์) | 1 | 5 | 6 |
| 5 | **DoctorToDept** (ผูกแผนก) | 0 | 4 | 4 |
| 6 | **Slots** (ช่วงเวลา/สแกนเนอร์) | 1 | 5 | 6 |
| 7 | **Booking** (ฝั่งคนไข้) | 4 | 6 | 10 |
| 8 | **Booking Management** (แอดมิน) | 2 | 5 | 7 |
| | **รวมทั้งสิ้น** | **15** | **33** | **48** |

*หมายเหตุ: ข้อมูลอัปเดต ณ วันที่ 11 มีนาคม 2569* 
