import re

# Dictionary for common medical and hospital terms transliteration
TRANSLIT_MAP = {
    # Titles & Roles
    "Doctor": "ด็อกเตอร์",
    "Dr.": "ด็อกเตอร์",
    "Staff": "สตาฟ",
    "Nurse": "เนิร์ส",
    "Patient": "เพเชียนท์",
    
    # Departments
    "Cardiology": "คาร์ดิโอโลจี",
    "Dermatology": "เดอร์มาโทโลจี",
    "Neurology": "นิวโรโลจี",
    "Pediatrics": "พีเดียทริคส์",
    "Orthopedics": "ออร์โธพิดิกส์",
    "Internal Medicine": "อินเทอร์นอล เมดิซีน",
    "Surgery": "เซอร์เจอรี",
    "OPD": "โอพีดี",
    "ER": "อีอาร์",
    "ICU": "ไอซียู",
    "Radiology": "เรดิโอโลจี",
    "Pharma": "ฟาร์มา",
    "Pharmacy": "ฟาร์มาซี",
    
    # Statuses
    "Active": "แอคทีฟ",
    "Cancelled": "แคนเซิลล์",
    "Completed": "คอมพลีตเท็ด",
    "Skipped": "สคิปป์",
    "Full": "ฟูล",
    "Pending": "เพนดิง",
    "Waiting": "เวตติง",
    
    # Common words
    "Queue": "คิว",
    "Slot": "สล็อต",
    "Booking": "บุ๊คกิ้ง",
    "History": "ฮิสทรี",
    "Department": "ดีพาร์ทเมนต์",
    "Service": "เซอร์วิส",
    "Center": "เซ็นเตอร์",
    "Medical": "เมดิคอล",
    "Checkup": "เช็คอัพ",
    "Clinic": "คลินิก",
}

def add_thai_reading(text):
    """
    Appends Thai pronunciation in parentheses if English words are found in the text.
    Example: "Cardiology" -> "Cardiology (คาร์ดิโอโลจี)"
    """
    if not text or not isinstance(text, str):
        return text
    
    # Simple check for English characters
    if not re.search('[a-zA-Z]', text):
        return text

    # Try exact match first
    if text in TRANSLIT_MAP:
        return f"{text} ({TRANSLIT_MAP[text]})"

    # Try sentence match by splitting
    words = text.split()
    translated_words = []
    has_english = False
    
    for word in words:
        # Strip punctuation
        clean_word = re.sub(r'[^\w\s]', '', word)
        if clean_word in TRANSLIT_MAP:
            translated_words.append(f"{word} ({TRANSLIT_MAP[clean_word]})")
            has_english = True
        elif re.search('[a-zA-Z]', word):
            # If word is English but not in map, just keep it (or we could try a heuristic)
            translated_words.append(word)
            has_english = True
        else:
            translated_words.append(word)
            
    if has_english:
        return " ".join(translated_words)
    
    return text
