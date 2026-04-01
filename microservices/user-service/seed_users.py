import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_service.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

def seed_users():
    users = [
        ('admin', 'admin@example.com', 'admin', 'admin'),
        ('founder', 'founder@example.com', 'password123', 'founder'),
        ('investor', 'investor@example.com', 'password123', 'investor'),
        ('user', 'user@example.com', 'password123', 'user'),
    ]
    
    for username, email, password, role in users:
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role,
                first_name=username.capitalize(),
                last_name='User'
            )
            print(f"Created user: {username} ({role})")
        else:
            print(f"User {username} already exists")

if __name__ == "__main__":
    seed_users()
