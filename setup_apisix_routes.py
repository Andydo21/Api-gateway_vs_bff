import requests
import json

ADMIN_KEY = "edd1c9f0-3353-3901-906d-73d197c72d2f"
APISIX_ADMIN_URL = "http://localhost:9180/apisix/admin"

headers = {
    "X-API-KEY": ADMIN_KEY,
    "Content-Type": "application/json"
}

def create_route(route_id, uri, upstream_nodes, name, enable_websocket=False):
    url = f"{APISIX_ADMIN_URL}/routes/{route_id}"
    data = {
        "name": name,
        "uri": uri,
        "upstream": {
            "type": "roundrobin",
            "nodes": upstream_nodes
        },
        "plugins": {
            "prometheus": {},
            "cors": {}
        },
        "enable_websocket": enable_websocket
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    if response.status_code in [200, 201]:
        print(f"Successfully created route: {name}")
    else:
        print(f"Failed to create route: {name}. Status: {response.status_code}, Error: {response.text}")

if __name__ == "__main__":
    # Routes for BFFs
    create_route("1", "/web/*", {"web-bff:3001": 1}, "Web-BFF")
    create_route("2", "/admin/*", {"admin-bff:3002": 1}, "Admin-BFF")
    
    # Route for UI / Auth (Frontend Service)
    create_route("3", "/ui/*", {"frontend-service:8000": 1}, "Frontend-UI-Service")
    
    # Route for Notifications (REST API)
    create_route("4", "/api/notifications/*", {"notification-service:4007": 1}, "Notification-Service-API")
    
    # Route for Notifications (WebSockets)
    create_route("5", "/ws/notifications/*", {"notification-service:4007": 1}, "Notification-Service-WS", enable_websocket=True)
    
    # Route for Health Check (replacing Nginx healthy endpoint)
    url = f"{APISIX_ADMIN_URL}/routes/6"
    data = {
        "name": "Health-Check",
        "uri": "/health",
        "plugins": {
            "fault-injection": {
                "abort": {
                    "http_status": 200,
                    "body": "APISIX Gateway is healthy"
                }
            }
        }
    }
    requests.put(url, headers=headers, data=json.dumps(data))
