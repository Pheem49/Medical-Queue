import os
import shutil

base_dir = r"c:\My document etc\Medical\Medical-Queue"
templates_dir = os.path.join(base_dir, "templates")

# Directories to create
dirs_to_create = [
    os.path.join(base_dir, "views"),
    os.path.join(base_dir, "services"),
    os.path.join(templates_dir, "auth"),
    os.path.join(templates_dir, "user"),
    os.path.join(templates_dir, "admin"),
]

for d in dirs_to_create:
    os.makedirs(d, exist_ok=True)

# Moves map: src -> dest
moves = {
    # auth
    "login.html": "auth/login.html",
    "register.html": "auth/register.html",
    "staff_login.html": "auth/staff_login.html",

    # user
    "home.html": "user/home.html",
    "booking.html": "user/booking.html",
    "history.html": "user/history.html",
    "mytickets.html": "user/mytickets.html",
    "notification.html": "user/notification.html",
    "terms.html": "user/terms.html",
    "privacy.html": "user/privacy.html",

    # admin
    "staff_checkin.html": "admin/scanner.html",
    "staff_patients.html": "admin/dashboard.html",
    "staff_doctors.html": "admin/doctors.html",
    "staff_history.html": "admin/history.html",
    "staff_base.html": "admin/staff_base.html", 
}

for src_name, dest_name in moves.items():
    src = os.path.join(templates_dir, src_name)
    dest = os.path.join(templates_dir, dest_name)
    if os.path.exists(src):
        with open(src, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update templates extending staff_base.html
        if "staff_base.html" in content:
            content = content.replace('{% extends "staff_base.html" %}', '{% extends "admin/staff_base.html" %}')
            content = content.replace("{% extends 'staff_base.html' %}", "{% extends 'admin/staff_base.html' %}")

        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # remove old
        os.remove(src)

print("Directories created and templates moved.")
