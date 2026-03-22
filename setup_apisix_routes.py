import requests
import json

ADMIN_KEY = "edd1c9f0-3353-3901-906d-73d197c72d2f"
APISIX_ADMIN_URL = "http://localhost:9180/apisix/admin"

headers = {
    "X-API-KEY": ADMIN_KEY,
    "Content-Type": "application/json"
}

def create_route(route_id, uri, upstream_nodes, name):
    url = f"{APISIX_ADMIN_URL}/routes/{route_id}"
    data = {
        "name": name,
        "uri": uri,
        "upstream": {
            "type": "roundrobin",
            "nodes": upstream_nodes
        },
        "plugins": {
            "prometheus": {}
        }
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
    
    # Route for Notifications (Direct)
    create_route("4", "/api/notifications/*", {"notification-service:4007": 1}, "Notification-Service")
