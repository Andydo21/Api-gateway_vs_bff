import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'product_service.settings')
django.setup()

from startup_app.models import Category, Startup, Investor


def seed_startup_data():
    # Categories
    ai_cat, _ = Category.objects.get_or_create(name='AI', description='Artificial Intelligence startups')
    fin_cat, _ = Category.objects.get_or_create(name='Fintech', description='Financial Technology startups')
    print("Categories ensured")

    # Startups
    s1, _ = Startup.objects.get_or_create(
        company_name='AI Revolution',
        defaults={
            'description': 'Revolutionizing AI locally',
            'industry': 'AI',
            'category': ai_cat,
            'status': 'APPROVED',
            'featured': True,
            'user_id': 2 # linked to founder user
        }
    )
    
    s2, _ = Startup.objects.get_or_create(
        company_name='Fintech Flow',
        defaults={
            'description': 'Smooth financial flows',
            'industry': 'Fintech',
            'category': fin_cat,
            'status': 'APPROVED',
            'user_id': 2
        }
    )
    print("Startups ensured")

    # Investor Profile
    Investor.objects.get_or_create(
        user_id=3, # linked to investor user
        defaults={
            'company_name': 'Global Ventures',
            'bio': 'Investing in the future of tech',
            'interests': 'AI, Fintech, Blockchain'
        }
    )
    print("Investor profile ensured")

if __name__ == "__main__":
    seed_startup_data()
