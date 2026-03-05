import urllib.request
import json

base_url = "http://127.0.0.1:5000"

def test_booking_endpoints():
    print("Testing Booking Endpoints...")
    
    # We might not be able to fully test without creating a User, Doctor, Department, and Slot first.
    # However, we can test if the endpoints at least return the expected errors for invalid data.
    
    # 1. Test GET /booking (UI Route)
    try:
        req = urllib.request.Request(f"{base_url}/booking")
        with urllib.request.urlopen(req) as response:
            print(f"GET /booking status: {response.getcode()}")
    except Exception as e:
        print(f"GET /booking failed: {e}")

    # 2. Test POST /api/bookings (Missing data)
    try:
        data = json.dumps({"slot_id": None, "id_users": None}).encode('utf-8')
        req = urllib.request.Request(f"{base_url}/api/bookings", data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req) as response:
            print(f"POST /api/bookings (missing data) status: {response.getcode()}")
    except urllib.error.HTTPError as e:
        print(f"POST /api/bookings (missing data) returned expected error: {e.code}")
    except Exception as e:
        print(f"POST /api/bookings (missing data) failed unexpectedly: {e}")
        
    print("Basic endpoint tests complete.")

if __name__ == "__main__":
    test_booking_endpoints()
