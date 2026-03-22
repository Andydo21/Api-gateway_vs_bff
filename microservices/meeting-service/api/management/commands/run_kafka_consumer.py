import json
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from confluent_kafka import Consumer, KafkaError
from api.models import Meeting, MeetingOutboxEvent
from django.db import transaction

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Runs Kafka consumer for Meeting Service to auto-create meetings'

    def handle(self, *args, **options):
        bootstrap_servers = getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        conf = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': 'meeting-service-group',
            'auto.offset.reset': 'earliest'
        }

        consumer = Consumer(conf)
        consumer.subscribe(['pitching_events'])

        self.stdout.write(self.style.SUCCESS(f'Started Kafka Consumer for Meeting Service (Brokers: {bootstrap_servers})'))
        
        try:
            while True:
                msg = consumer.poll(1.0)

                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        logger.error(f"Consumer error: {msg.error()}")
                        break

                # Process message
                try:
                    payload = json.loads(msg.value().decode('utf-8'))
                    event_type = payload.get('event_type')
                    data = payload.get('data')

                    if event_type == 'slot_confirmed':
                        self.auto_create_meeting(data)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except KeyboardInterrupt:
            pass
        finally:
            consumer.close()

    def auto_create_meeting(self, booking_data):
        """Automatically create a meeting when a booking is confirmed"""
        import requests
        from django.utils.dateparse import parse_datetime

        booking_id = booking_data.get('id')
        pitch_slot_id = booking_data.get('pitch_slot_id')
        
        self.stdout.write(self.style.NOTICE(f" [KAFKA] Nhận sự kiện Booking #{booking_id}. Đang lấy thông tin lịch trình..."))

        # Fetch slot details from Scheduling Service
        scheduling_url = getattr(settings, 'SCHEDULING_SERVICE_URL', 'http://localhost:4008')
        start_time = None
        end_time = None
        
        try:
            res = requests.get(f"{scheduling_url}/pitch-slots/{pitch_slot_id}/", timeout=5)
            if res.status_code == 200:
                slot_data = res.json()
                start_time = slot_data.get('start_time')
                end_time = slot_data.get('end_time')
        except Exception as e:
            logger.error(f"Error fetching slot details: {e}")

        # Fallback to current time if fetch fails
        if not start_time:
            from django.utils import timezone
            start_time = timezone.now()
            end_time = start_time + timezone.timedelta(minutes=30)
            self.stdout.write(self.style.WARNING(f" ⚠️ Không lấy được thông tin từ Scheduling Service cho Slot #{pitch_slot_id}. Dùng thời gian mặc định."))

        meeting_url = f"https://zoom.us/j/{booking_id}12345678"
        
        try:
            with transaction.atomic():
                meeting = Meeting.objects.create(
                    booking_id=booking_id,
                    meeting_url=meeting_url,
                    meeting_type='ZOOM',
                    start_time=start_time,
                    end_time=end_time,
                    status='ONGOING'
                )
                
                # Broadcast meeting creation
                MeetingOutboxEvent.objects.create(
                    event_type='meeting_auto_created',
                    payload={
                        'meeting_id': meeting.id,
                        'booking_id': booking_id,
                        'meeting_url': meeting_url
                    }
                )
            self.stdout.write(self.style.SUCCESS(f" ✅ Meeting cho Booking #{booking_id} đã được tạo tự động: {meeting_url}"))
        except Exception as e:
            logger.error(f"Error creating meeting: {e}")
            with transaction.atomic():
                MeetingOutboxEvent.objects.create(
                    event_type='meeting_failed',
                    payload={
                        'booking_id': booking_id,
                        'pitch_slot_id': pitch_slot_id,
                        'reason': str(e)
                    }
                )
            self.stdout.write(self.style.ERROR(f" ❌ [SAGA] Tạo Meeting thất bại cho Booking #{booking_id}. Đang báo lỗi..."))
