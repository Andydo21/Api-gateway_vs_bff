"""
Script to create sample data for E-Commerce system
Run after all services are up and migrations are complete
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"
USER_SERVICE = "http://localhost:4001"  # Direct access to user-service
PRODUCT_SERVICE = "http://localhost:4002"
INVENTORY_SERVICE = "http://localhost:4005"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def check_service_health():
    """Check if services are running"""
    print_section("Checking Services Health")
    
    try:
        response = requests.get(f"{BASE_URL}/health/", timeout=5)
        if response.status_code == 200:
            print("✅ API Gateway is running")
        else:
            print("❌ API Gateway returned error")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API Gateway: {e}")
        return False
    
    return True

def create_users():
    """Create sample users"""
    print_section("Creating Sample Users")
    
    users_data = [
        {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "password123",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "0901234567"
        },
        {
            "username": "jane_smith",
            "email": "jane@example.com",
            "password": "password123",
            "first_name": "Jane",
            "last_name": "Smith",
            "phone": "0909876543"
        },
        {
            "username": "admin_user",
            "email": "admin@example.com",
            "password": "admin123",
            "first_name": "Admin",
            "last_name": "User",
            "phone": "0900000000"
        }
    ]
    
    created_users = []
    for user in users_data:
        try:
            response = requests.post(f"{USER_SERVICE}/register/", json=user)
            if response.status_code == 201:
                result = response.json()
                created_users.append(result)
                print(f"✅ Created user: {user['username']}")
            else:
                print(f"⚠️  User {user['username']} may already exist or error: {response.text}")
        except Exception as e:
            print(f"❌ Error creating user {user['username']}: {e}")
    
    return created_users

def create_categories():
    """Create product categories"""
    print_section("Creating Product Categories")
    
    categories = [
        {
            "name": "Điện thoại",
            "description": "Smartphone và thiết bị di động"
        },
        {
            "name": "Laptop",
            "description": "Máy tính xách tay"
        },
        {
            "name": "Tablet",
            "description": "Máy tính bảng"
        },
        {
            "name": "Phụ kiện",
            "description": "Phụ kiện điện tử"
        },
        {
            "name": "Đồng hồ thông minh",
            "description": "Smartwatch và wearables"
        }
    ]
    
    created_categories = []
    for cat in categories:
        try:
            response = requests.post(f"{PRODUCT_SERVICE}/categories/", json=cat)
            if response.status_code in [200, 201]:
                result = response.json()
                created_categories.append(result.get('data', result))
                print(f"✅ Created category: {cat['name']}")
            else:
                print(f"⚠️  Category {cat['name']} may already exist")
        except Exception as e:
            print(f"❌ Error creating category {cat['name']}: {e}")
    
    return created_categories

def create_products():
    """Create sample products"""
    print_section("Creating Sample Products")
    
    products = [
        {
            "name": "iPhone 15 Pro Max",
            "description": "Apple iPhone 15 Pro Max 256GB - Titanium tự nhiên",
            "price": "32990000",
            "category": 1,
            "stock": 50,
            "featured": True,
            "rating": 4.8
        },
        {
            "name": "Samsung Galaxy S24 Ultra",
            "description": "Samsung Galaxy S24 Ultra 12GB/256GB - Titanium Gray",
            "price": "29990000",
            "category": 1,
            "stock": 45,
            "featured": True,
            "rating": 4.7
        },
        {
            "name": "MacBook Pro M3 Max",
            "description": "MacBook Pro 16-inch M3 Max 48GB RAM 1TB SSD",
            "price": "89990000",
            "category": 2,
            "stock": 20,
            "featured": True,
            "rating": 4.9
        },
        {
            "name": "Dell XPS 15",
            "description": "Dell XPS 15 9530 i7-13700H 32GB RAM 1TB SSD RTX 4060",
            "price": "54990000",
            "category": 2,
            "stock": 25,
            "featured": True,
            "rating": 4.6
        },
        {
            "name": "iPad Pro 12.9",
            "description": "iPad Pro 12.9-inch M2 WiFi 256GB - Space Gray",
            "price": "31990000",
            "category": 3,
            "stock": 30,
            "featured": True,
            "rating": 4.8
        },
        {
            "name": "Samsung Galaxy Tab S9",
            "description": "Samsung Galaxy Tab S9 Ultra 12GB/256GB",
            "price": "27990000",
            "category": 3,
            "stock": 35,
            "featured": False,
            "rating": 4.5
        },
        {
            "name": "AirPods Pro 2",
            "description": "Apple AirPods Pro Gen 2 with USB-C",
            "price": "6490000",
            "category": 4,
            "stock": 100,
            "featured": True,
            "rating": 4.7
        },
        {
            "name": "Sony WH-1000XM5",
            "description": "Sony WH-1000XM5 Wireless Noise Cancelling Headphones",
            "price": "8990000",
            "category": 4,
            "stock": 60,
            "featured": True,
            "rating": 4.9
        },
        {
            "name": "Apple Watch Series 9",
            "description": "Apple Watch Series 9 45mm GPS - Starlight Aluminum",
            "price": "11490000",
            "category": 5,
            "stock": 40,
            "featured": True,
            "rating": 4.6
        },
        {
            "name": "Samsung Galaxy Watch 6",
            "description": "Samsung Galaxy Watch 6 Classic 47mm LTE",
            "price": "9990000",
            "category": 5,
            "stock": 50,
            "featured": False,
            "rating": 4.5
        }
    ]
    
    created_products = []
    for product in products:
        try:
            response = requests.post(f"{PRODUCT_SERVICE}/products/", json=product)
            if response.status_code in [200, 201]:
                result = response.json()
                product_data = result.get('data', result)
                created_products.append(product_data)
                print(f"✅ Created product: {product['name']}")
            else:
                print(f"⚠️  Error creating product {product['name']}: {response.text}")
        except Exception as e:
            print(f"❌ Error creating product {product['name']}: {e}")
    
    return created_products

def create_inventory(products):
    """Create inventory for products"""
    print_section("Creating Inventory Records")
    
    for product in products:
        inventory_data = {
            "product_id": product['id'],
            "product_name": product['name'],
            "available_quantity": product.get('stock', 0),
            "reserved_quantity": 0,
            "reorder_level": 10
        }
        
        try:
            response = requests.post(f"{INVENTORY_SERVICE}/inventory/", json=inventory_data)
            if response.status_code in [200, 201]:
                print(f"✅ Created inventory for: {product['name']}")
            else:
                print(f"⚠️  Inventory may already exist for: {product['name']}")
        except Exception as e:
            print(f"❌ Error creating inventory for {product['name']}: {e}")

def create_reviews(products):
    """Create sample reviews"""
    print_section("Creating Sample Reviews")
    
    reviews = [
        {"product_id": 1, "user_id": 1, "rating": 5, "comment": "Sản phẩm tuyệt vời! Rất đáng tiền"},
        {"product_id": 1, "user_id": 2, "rating": 4, "comment": "Máy đẹp, pin trâu, camera chất lượng"},
        {"product_id": 2, "user_id": 1, "rating": 5, "comment": "Samsung Galaxy S24 Ultra rất xịn"},
        {"product_id": 3, "user_id": 2, "rating": 5, "comment": "MacBook Pro M3 Max cực mạnh"},
        {"product_id": 7, "user_id": 1, "rating": 4, "comment": "AirPods Pro 2 nghe hay, chống ồn tốt"},
    ]
    
    for review in reviews:
        try:
            response = requests.post(f"{PRODUCT_SERVICE}/reviews/", json=review)
            if response.status_code in [200, 201]:
                print(f"✅ Created review for product #{review['product_id']}")
            else:
                print(f"⚠️  Error creating review: {response.text}")
        except Exception as e:
            print(f"❌ Error creating review: {e}")

def main():
    """Main function"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     E-COMMERCE SAMPLE DATA GENERATOR                     ║
    ║     API Gateway + BFF + Microservices Architecture       ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Check if services are running
    if not check_service_health():
        print("\n❌ Services are not running. Please start Docker Compose first:")
        print("   docker-compose up")
        sys.exit(1)
    
    # Create data
    users = create_users()
    categories = create_categories()
    products = create_products()
    
    if products:
        create_inventory(products)
        create_reviews(products)
    
    # Summary
    print_section("Summary")
    print(f"✅ Users created: {len(users)}")
    print(f"✅ Categories created: {len(categories)}")
    print(f"✅ Products created: {len(products)}")
    
    print("\n" + "="*60)
    print("  🎉 Sample data creation completed successfully!")
    print("="*60)
    print("\nYou can now:")
    print("  1. Open http://localhost:8080 (Web Frontend)")
    print("  2. Open http://localhost:8081/admin.html (Admin Panel)")
    print("  3. Test API at http://localhost:8000")
    print("\nTest credentials:")
    print("  Username: john_doe")
    print("  Password: password123")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
