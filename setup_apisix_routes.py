# [SCRUM-4] API Gateway: APISIX Route Configuration & Service Discovery
import requests
import json

ADMIN_KEY = "edd1c9f0-3353-3901-906d-73d197c72d2f"
APISIX_ADMIN_URL = "http://localhost:9180/apisix/admin"

headers = {
    "X-API-KEY": ADMIN_KEY,
    "Content-Type": "application/json"
}

def create_route(route_id, uri, upstream_nodes, name, enable_websocket=False, use_jwt=False, priority=0):
    url = f"{APISIX_ADMIN_URL}/routes/{route_id}"
    
    plugins = {
        "prometheus": {},
        "cors": {},
        "limit-req": {
            "rate": 10,
            "burst": 5,
            "key": "remote_addr",
            "rejected_code": 429
        },
        "file-logger": {
            "path": "/usr/local/apisix/logs/access.log"
        },
        "api-breaker": {
            "break_response_code": 502,
            "max_breaker_sec": 30,
            "unhealthy": {
                "http_statuses": [500, 503, 504],
                "failures": 3
            },
            "healthy": {
                "http_statuses": [200, 201],
                "successes": 3
            }
        }
    }
    
    if use_jwt:
        plugins["jwt-auth"] = {}
        
    data = {
        "name": name,
        "uri": uri,
        "priority": priority,
        "upstream": {
            "type": "roundrobin",
            "nodes": upstream_nodes
        },
        "plugins": plugins,
        "enable_websocket": enable_websocket
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    if response.status_code in [200, 201]:
        print(f"Successfully created route: {name}")
    else:
        print(f"Failed to create route: {name}. Status: {response.status_code}, Error: {response.text}")

if __name__ == "__main__":
    # Routes for BFFs
    # NOTE: jwt-auth disabled because APISIX's jwt-auth plugin uses its own 
    # consumer/key/secret system which is incompatible with Django simplejwt tokens.
    # Auth is handled by the BFF reading the Authorization header from the frontend.
    create_route("1", "/web/*", {"web-bff:3001": 1}, "Web-BFF", use_jwt=False)
    
    create_route("2", "/admin/*", {"admin-bff:3002": 1}, "Admin-BFF", use_jwt=False)
    
    # Route for UI / Auth (Frontend Service)
    create_route("3", "/ui/*", {"frontend-service:8000": 1}, "Frontend-UI-Service")
    
    # Route for Notifications (REST API)
    create_route("4", "/api/notifications/*", {"notification-service:4007": 1}, "Notification-Service-API")
    
    # Route for Notifications (WebSockets)
    create_route("5", "/ws/notifications/*", {"notification-service:4007": 1}, "Notification-Service-WS", enable_websocket=True)
    
    # Route for Health Check
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
            },
            "file-logger": {
                "path": "/usr/local/apisix/logs/access.log"
            }
        }
    }
    requests.put(url, headers=headers, data=json.dumps(data))
