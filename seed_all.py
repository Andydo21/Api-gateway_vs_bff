"""
Comprehensive Seed Script for all Microservices.
Runs each service's seed via docker-compose exec.
"""
import subprocess
import sys

# ============================================================
# 1. USER SERVICE - Users
# ============================================================
USER_SEED = r"""
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_service.settings')
django.setup()
from user_app.models import User

if User.objects.count() > 1:
    print('Users already seeded, skipping...')
else:
    users_data = [
        {'username': 'john_doe', 'email': 'john@example.com', 'role': 'investor', 'phone': '0901234567'},
        {'username': 'jane_smith', 'email': 'jane@example.com', 'role': 'founder', 'phone': '0912345678'},
        {'username': 'bob_investor', 'email': 'bob@example.com', 'role': 'investor', 'phone': '0923456789'},
        {'username': 'alice_founder', 'email': 'alice@example.com', 'role': 'founder', 'phone': '0934567890'},
        {'username': 'charlie_user', 'email': 'charlie@example.com', 'role': 'user', 'phone': '0945678901'},
        {'username': 'david_investor', 'email': 'david@example.com', 'role': 'investor', 'phone': '0956789012'},
        {'username': 'eva_founder', 'email': 'eva@example.com', 'role': 'founder', 'phone': '0967890123'},
        {'username': 'frank_user', 'email': 'frank@example.com', 'role': 'user', 'phone': '0978901234'},
    ]
    for u in users_data:
        user = User.objects.create_user(username=u['username'], email=u['email'], password='password123', role=u['role'], phone=u['phone'])
        print(f'  Created user: {u["username"]} (role: {u["role"]})')
    print(f'Total users: {User.objects.count()}')
"""

# ============================================================
# 2. STARTUP SERVICE - Categories, Startups, Investors, Reviews
# ============================================================
STARTUP_SEED = r"""
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'product_service.settings')
django.setup()
from startup_app.models import Category, Startup, Investor, Review

if Startup.objects.count() > 0:
    print('Startups already seeded, skipping...')
else:
    # Categories
    cats = {}
    for name, desc in [
        ('AI & Machine Learning', 'Artificial Intelligence and ML startups'),
        ('FinTech', 'Financial Technology startups'),
        ('HealthTech', 'Health and Medical Technology'),
        ('EdTech', 'Education Technology'),
        ('E-Commerce', 'Online Commerce platforms'),
        ('SaaS', 'Software as a Service'),
        ('CleanTech', 'Clean Energy and Environment'),
        ('Gaming', 'Game Development and Esports'),
    ]:
        cats[name] = Category.objects.create(name=name, description=desc)
        print(f'  Created category: {name}')

    # Startups
    startups_data = [
        {'company_name': 'NeuraTech AI', 'description': 'Platform tri tue nhan tao cho doanh nghiep vua va nho, tu dong hoa quy trinh kinh doanh.', 'industry': 'AI & Machine Learning', 'user_id': 3, 'website': 'https://neuratech.ai', 'featured': True, 'status': 'APPROVED', 'image_url': 'https://picsum.photos/seed/neura/400/300'},
        {'company_name': 'PayFlow', 'description': 'Giai phap thanh toan so tich hop cho thi truong Dong Nam A.', 'industry': 'FinTech', 'user_id': 4, 'website': 'https://payflow.vn', 'featured': True, 'status': 'APPROVED', 'image_url': 'https://picsum.photos/seed/payflow/400/300'},
        {'company_name': 'MediScan', 'description': 'Ung dung AI chan doan hinh anh y khoa, ho tro bac si phat hien benh som.', 'industry': 'HealthTech', 'user_id': 3, 'website': 'https://mediscan.health', 'featured': True, 'status': 'APPROVED', 'image_url': 'https://picsum.photos/seed/medi/400/300'},
        {'company_name': 'EduVerse', 'description': 'Nen tang hoc truc tuyen voi cong nghe VR/AR, trai nghiem hoc tap hoan toan moi.', 'industry': 'EdTech', 'user_id': 5, 'website': 'https://eduverse.io', 'featured': True, 'status': 'APPROVED', 'image_url': 'https://picsum.photos/seed/edu/400/300'},
        {'company_name': 'ShopNow', 'description': 'San thuong mai dien tu B2B ket noi nha cung cap va nha ban le.', 'industry': 'E-Commerce', 'user_id': 4, 'website': 'https://shopnow.vn', 'featured': False, 'status': 'APPROVED', 'image_url': 'https://picsum.photos/seed/shop/400/300'},
        {'company_name': 'CloudMetrics', 'description': 'Cong cu phan tich du lieu va giam sat he thong cho doanh nghiep.', 'industry': 'SaaS', 'user_id': 7, 'website': 'https://cloudmetrics.io', 'featured': True, 'status': 'APPROVED', 'image_url': 'https://picsum.photos/seed/cloud/400/300'},
        {'company_name': 'GreenPower', 'description': 'Giai phap nang luong mat troi thong minh cho ho gia dinh va doanh nghiep.', 'industry': 'CleanTech', 'user_id': 5, 'website': 'https://greenpower.vn', 'featured': False, 'status': 'APPROVED', 'image_url': 'https://picsum.photos/seed/green/400/300'},
        {'company_name': 'GameForge', 'description': 'Studio phat trien game mobile hang dau Viet Nam.', 'industry': 'Gaming', 'user_id': 7, 'website': 'https://gameforge.vn', 'featured': True, 'status': 'APPROVED', 'image_url': 'https://picsum.photos/seed/game/400/300'},
        {'company_name': 'DataShield', 'description': 'Nen tang bao mat du lieu va phong chong tan cong mang cho doanh nghiep.', 'industry': 'SaaS', 'user_id': 3, 'website': 'https://datashield.io', 'featured': False, 'status': 'PENDING', 'image_url': 'https://picsum.photos/seed/shield/400/300'},
        {'company_name': 'FarmTech', 'description': 'IoT va AI cho nong nghiep thong minh, tang nang suat canh tac.', 'industry': 'CleanTech', 'user_id': 4, 'website': 'https://farmtech.vn', 'featured': False, 'status': 'PENDING', 'image_url': 'https://picsum.photos/seed/farm/400/300'},
    ]
    created_startups = []
    for s in startups_data:
        cat = cats.get(s['industry'])
        startup = Startup.objects.create(
            company_name=s['company_name'], description=s['description'], industry=s['industry'],
            user_id=s['user_id'], website=s['website'], featured=s['featured'], status=s['status'],
            category=cat, image_url=s['image_url']
        )
        created_startups.append(startup)
        print(f'  Created startup: {s["company_name"]}')

    # Investors
    for uid, name, bio, interests in [
        (2, 'Alpha Ventures', 'Quy dau tu tap trung vao AI va cong nghe', 'AI,SaaS,FinTech'),
        (3, 'Mekong Capital', 'Quy dau tu hang dau Dong Nam A', 'E-Commerce,FinTech,HealthTech'),
        (6, 'Future Fund', 'Dau tu vao cac startup giai doan dau', 'EdTech,CleanTech,Gaming'),
    ]:
        Investor.objects.create(user_id=uid, company_name=name, bio=bio, interests=interests)
        print(f'  Created investor: {name}')

    # Reviews
    import random
    comments = ['Tuyet voi!', 'Mot y tuong sang tao.', 'Can cai thien them.', 'Rat tiem nang!', 'Doi ngu tot, san pham dang chu y.', 'Mong cho ngay ra mat chinh thuc.']
    for startup in created_startups[:6]:
        for uid in [2, 5, 6, 8]:
            Review.objects.create(startup=startup, user_id=uid, username=f'user_{uid}', rating=random.randint(3, 5), comment=random.choice(comments))
    print(f'  Created {Review.objects.count()} reviews')
"""

# ============================================================
# 3. SCHEDULING SERVICE - AvailabilityTemplates, PitchSlots
# ============================================================
SCHEDULING_SEED = r"""
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scheduling_service.settings')
django.setup()
from scheduling_app.models import AvailabilityTemplate, PitchSlot
from datetime import datetime, timedelta, time
from django.utils import timezone

if PitchSlot.objects.count() > 0:
    print('Scheduling already seeded, skipping...')
else:
    # Availability Templates for investors
    for inv_id in [2, 3, 6]:
        for day in range(0, 5):  # Mon-Fri
            AvailabilityTemplate.objects.create(investor_id=inv_id, day_of_week=day, start_time=time(9, 0), end_time=time(12, 0))
            AvailabilityTemplate.objects.create(investor_id=inv_id, day_of_week=day, start_time=time(14, 0), end_time=time(17, 0))
    print(f'  Created {AvailabilityTemplate.objects.count()} availability templates')

    # PitchSlots for next 7 days
    now = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    statuses = ['AVAILABLE', 'AVAILABLE', 'AVAILABLE', 'BOOKED']
    slot_count = 0
    for inv_id in [2, 3, 6]:
        for day_offset in range(1, 8):
            base = now + timedelta(days=day_offset)
            if base.weekday() >= 5: continue
            for hour in [9, 10, 11, 14, 15, 16]:
                import random
                st = base.replace(hour=hour)
                PitchSlot.objects.create(investor_id=inv_id, start_time=st, end_time=st + timedelta(hours=1), status=random.choice(statuses))
                slot_count += 1
    print(f'  Created {slot_count} pitch slots')
"""

# ============================================================
# 4. BOOKING SERVICE - PitchRequests, PitchBookings
# ============================================================
BOOKING_SEED = r"""
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'booking_service.settings')
django.setup()
from booking_app.models import PitchRequest, PitchBooking

if PitchRequest.objects.count() > 0:
    print('Bookings already seeded, skipping...')
else:
    requests_data = [
        {'startup_id': 1, 'title': 'NeuraTech AI - Series A Pitch', 'pitch_deck_url': 'https://drive.google.com/neuratech', 'status': 'APPROVED'},
        {'startup_id': 2, 'title': 'PayFlow - Seed Round', 'pitch_deck_url': 'https://drive.google.com/payflow', 'status': 'SCHEDULED'},
        {'startup_id': 3, 'title': 'MediScan - Pre-Series A', 'pitch_deck_url': 'https://drive.google.com/mediscan', 'status': 'REGISTERED'},
        {'startup_id': 4, 'title': 'EduVerse - Angel Round', 'pitch_deck_url': 'https://drive.google.com/eduverse', 'status': 'COMPLETED'},
        {'startup_id': 6, 'title': 'CloudMetrics - Series B', 'pitch_deck_url': 'https://drive.google.com/cloudmetrics', 'status': 'APPROVED'},
    ]
    for pr in requests_data:
        req = PitchRequest.objects.create(**pr)
        print(f'  Created pitch request: {pr["title"]}')
    
    # Create bookings for scheduled/completed requests
    PitchBooking.objects.create(pitch_request_id=2, pitch_slot_id=1, status='SCHEDULED')
    PitchBooking.objects.create(pitch_request_id=4, pitch_slot_id=5, status='COMPLETED')
    print(f'  Created {PitchBooking.objects.count()} pitch bookings')
"""

# ============================================================
# 5. MEETING SERVICE - Meetings
# ============================================================
MEETING_SEED = r"""
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meeting_service.settings')
django.setup()
from meeting_app.models import Meeting
from django.utils import timezone
from datetime import timedelta

if Meeting.objects.count() > 0:
    print('Meetings already seeded, skipping...')
else:
    now = timezone.now()
    meetings = [
        {'booking_id': 1, 'meeting_url': 'https://zoom.us/j/123456789', 'meeting_type': 'ZOOM', 'start_time': now + timedelta(days=2, hours=9), 'end_time': now + timedelta(days=2, hours=10), 'status': 'ONGOING'},
        {'booking_id': 2, 'meeting_url': 'https://meet.google.com/abc-defg-hij', 'meeting_type': 'GOOGLE_MEET', 'start_time': now - timedelta(days=3, hours=14), 'end_time': now - timedelta(days=3, hours=15), 'status': 'ENDED'},
    ]
    for m in meetings:
        Meeting.objects.create(**m)
        print(f'  Created meeting: {m["meeting_type"]} for booking #{m["booking_id"]}')
"""

# ============================================================
# 6. FEEDBACK SERVICE - Feedbacks, InvestmentInterests
# ============================================================
FEEDBACK_SEED = r"""
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'feedback_service.settings')
django.setup()
from feedback_app.models import Feedback, InvestmentInterest

if Feedback.objects.count() > 0:
    print('Feedback already seeded, skipping...')
else:
    feedbacks = [
        {'booking_id': 2, 'investor_id': 2, 'rating': 5, 'comment': 'Doi ngu rat an tuong, san pham co tiem nang lon.'},
        {'booking_id': 2, 'investor_id': 3, 'rating': 4, 'comment': 'Y tuong tot, can lam ro hon ve mo hinh doanh thu.'},
    ]
    for f in feedbacks:
        Feedback.objects.create(**f)
        print(f'  Created feedback from investor #{f["investor_id"]}')

    interests = [
        {'booking_id': 2, 'investor_id': 2, 'status': 'INTERESTED', 'note': 'Se dau tu 500K USD cho vong Seed.'},
        {'booking_id': 2, 'investor_id': 3, 'status': 'FOLLOW_UP', 'note': 'Can xem them bao cao tai chinh Q2.'},
    ]
    for i in interests:
        InvestmentInterest.objects.create(**i)
        print(f'  Created interest: {i["status"]} from investor #{i["investor_id"]}')
"""

# ============================================================
# 7. FUNDING SERVICE - Payments
# ============================================================
FUNDING_SEED = r"""
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payment_service.settings')
django.setup()
from funding_app.models import Payment

if Payment.objects.count() > 0:
    print('Payments already seeded, skipping...')
else:
    payments = [
        {'reference_id': 1, 'user_id': 2, 'amount': 5000000, 'payment_method': 'bank_transfer', 'status': 'completed', 'transaction_id': 'TXN-001-VN'},
        {'reference_id': 2, 'user_id': 3, 'amount': 2500000, 'payment_method': 'credit_card', 'status': 'completed', 'transaction_id': 'TXN-002-VN'},
        {'reference_id': 3, 'user_id': 6, 'amount': 1500000, 'payment_method': 'paypal', 'status': 'pending', 'transaction_id': 'TXN-003-VN'},
        {'reference_id': 4, 'user_id': 2, 'amount': 10000000, 'payment_method': 'bank_transfer', 'status': 'processing', 'transaction_id': 'TXN-004-VN'},
    ]
    for p in payments:
        Payment.objects.create(**p)
        print(f'  Created payment: {p["transaction_id"]} ({p["status"]})')
"""

# ============================================================
# 8. RESOURCE SERVICE - EventResources
# ============================================================
RESOURCE_SEED = r"""
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resource_service.settings')
django.setup()
from resource_app.models import EventResource

if EventResource.objects.count() > 0:
    print('Resources already seeded, skipping...')
else:
    resources = [
        {'startup_id': 1, 'startup_name': 'NeuraTech AI', 'available_quantity': 50, 'reserved_quantity': 10},
        {'startup_id': 2, 'startup_name': 'PayFlow', 'available_quantity': 30, 'reserved_quantity': 5},
        {'startup_id': 3, 'startup_name': 'MediScan', 'available_quantity': 20, 'reserved_quantity': 8},
        {'startup_id': 4, 'startup_name': 'EduVerse', 'available_quantity': 40, 'reserved_quantity': 15},
        {'startup_id': 6, 'startup_name': 'CloudMetrics', 'available_quantity': 25, 'reserved_quantity': 3},
    ]
    for r in resources:
        EventResource.objects.create(**r)
        print(f'  Created resource for: {r["startup_name"]}')
"""

# ============================================================
# 9. NOTIFICATION SERVICE - Notifications
# ============================================================
NOTIFICATION_SEED = r"""
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_service.settings')
django.setup()
from notification_app.models import Notification

if Notification.objects.count() > 0:
    print('Notifications already seeded, skipping...')
else:
    notifs = [
        {'user_id': 1, 'message': 'Chao mung ban den voi Startup Hub!', 'notification_type': 'info'},
        {'user_id': 1, 'message': 'Ho so Pitch cua NeuraTech AI da duoc duyet.', 'notification_type': 'success'},
        {'user_id': 2, 'message': 'Ban co 3 slot pitch moi trong tuan nay.', 'notification_type': 'info'},
        {'user_id': 2, 'message': 'Thanh toan 5,000,000 VND da thanh cong.', 'notification_type': 'success'},
        {'user_id': 3, 'message': 'Startup PayFlow cua ban da nhan duoc 1 don xin pitch moi.', 'notification_type': 'info'},
        {'user_id': 4, 'message': 'Cuoc hop Zoom voi Alpha Ventures da duoc len lich.', 'notification_type': 'success'},
        {'user_id': 5, 'message': 'Canh bao: Tai khoan sap het han premium.', 'notification_type': 'warning'},
        {'user_id': 6, 'message': 'Startup MediScan da cap nhat ho so moi.', 'notification_type': 'info'},
    ]
    for n in notifs:
        Notification.objects.create(**n)
        print(f'  Created notification for user #{n["user_id"]}: {n["message"][:40]}...')
"""

# ============================================================
# 10. MATCHMAKING SERVICE - UserInteractions, StartupSimilarities
# ============================================================
MATCHMAKING_SEED = r"""
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'matchmaking_service.settings')
django.setup()
from matchmaking_app.models import UserInteraction, StartupSimilarity

if UserInteraction.objects.count() > 0:
    print('Matchmaking already seeded, skipping...')
else:
    import random
    # User interactions
    interactions = []
    for uid in [1, 2, 3, 5, 6, 8]:
        for sid in random.sample(range(1, 9), 4):
            itype = random.choice(['view', 'click', 'like', 'pitch_request'])
            weight = {'view': 1.0, 'click': 2.0, 'like': 3.0, 'pitch_request': 5.0}[itype]
            UserInteraction.objects.create(user_id=uid, startup_id=sid, interaction_type=itype, weight=weight)
    print(f'  Created {UserInteraction.objects.count()} user interactions')

    # Startup similarities
    pairs = [(1,3,0.85), (1,6,0.72), (2,5,0.68), (3,4,0.55), (4,8,0.78), (6,1,0.72), (7,8,0.90), (2,6,0.60)]
    for s1, s2, score in pairs:
        StartupSimilarity.objects.create(startup_id=s1, similar_startup_id=s2, similarity_score=score)
    print(f'  Created {StartupSimilarity.objects.count()} startup similarities')
"""

# ============================================================
# RUNNER
# ============================================================
SEEDS = [
    ('user-service', USER_SEED),
    ('startup-service', STARTUP_SEED),
    ('scheduling-service', SCHEDULING_SEED),
    ('booking-service', BOOKING_SEED),
    ('meeting-service', MEETING_SEED),
    ('feedback-service', FEEDBACK_SEED),
    ('funding-service', FUNDING_SEED),
    ('resource-service', RESOURCE_SEED),
    ('notification-service', NOTIFICATION_SEED),
    ('matchmaking-service', MATCHMAKING_SEED),
]

def run_seed(service_name, script):
    print(f'\n{"="*50}')
    print(f'  Seeding: {service_name}')
    print(f'{"="*50}')
    cmd = ['docker-compose', 'exec', '-T', service_name, 'python', '-c', script]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=r'd:\Django_project\api-gateway_vs_bff')
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        print(f'  ERROR: {result.stderr[-300:] if result.stderr else "Unknown error"}')
    return result.returncode == 0

if __name__ == '__main__':
    print('🌱 Starting comprehensive data seed...\n')
    success = 0
    failed = 0
    for name, script in SEEDS:
        if run_seed(name, script):
            success += 1
        else:
            failed += 1
    print(f'\n{"="*50}')
    print(f'✅ Completed: {success} services seeded')
    if failed:
        print(f'❌ Failed: {failed} services')
    print(f'{"="*50}')
