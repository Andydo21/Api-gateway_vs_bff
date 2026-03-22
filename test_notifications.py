import requests
import json
import time

BASE_URL = "http://localhost:8000/notifications"
USER_ID = 1

def test_notification_flow():
    print(f"🚀 Starting API check for user_id={USER_ID}...\n")

    # 1. Send a notification (Internal service simulation)
    # Since this is an internal API, we call it via the Gateway which proxies to the service
    print("1. Sending notification...")
    payload = {
        "user_id": USER_ID,
        "message": f"Test notification at {time.strftime('%H:%M:%S')}",
        "notification_type": "success"
    }
    try:
        resp = requests.post(f"{BASE_URL}/send/", json=payload, timeout=5)
        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.json()}")
    except Exception as e:
        print(f"   ❌ Error sending: {e}")

    # 2. List notifications
    print("\n2. Fetching notification list...")
    try:
        resp = requests.get(f"{BASE_URL}/list/", params={"user_id": USER_ID}, timeout=5)
        print(f"   Status: {resp.status_code}")
        data = resp.json()
        if data.get('success'):
            items = data.get('data', [])
            print(f"   Items found: {len(items)}")
            if items:
                latest = items[0]
                print(f"   Latest: [{latest['id']}] {latest['message']} (Read: {latest['is_read']})")
                
                # 3. Mark as read
                print(f"\n3. Marking notification {latest['id']} as read...")
                read_resp = requests.put(f"{BASE_URL}/{latest['id']}/read/", timeout=5)
                print(f"   Status: {read_resp.status_code}")
                print(f"   Response: {read_resp.json()}")
        else:
            print(f"   ❌ Error: {data}")
    except Exception as e:
        print(f"   ❌ Error listing: {e}")

if __name__ == "__main__":
    test_notification_flow()
