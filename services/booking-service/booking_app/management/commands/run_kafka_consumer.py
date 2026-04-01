import json
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from confluent_kafka import Consumer, KafkaError
from booking_app.models import PitchBooking, BookingOutboxEvent
from django.db import transaction

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Runs Kafka consumer for Booking Service to handle Saga flow completion/failure'

    def handle(self, *args, **options):
        bootstrap_servers = getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        conf = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': 'booking-service-group',
            'auto.offset.reset': 'earliest'
        }

        consumer = Consumer(conf)
        consumer.subscribe(['pitching_events'])

        self.stdout.write(self.style.SUCCESS(f'Started Kafka Consumer for Booking Service (Brokers: {bootstrap_servers})'))
        
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

                    if event_type == 'meeting_auto_created':
                        self.handle_saga_success(data)
                    elif event_type in ['slot_failed', 'meeting_failed']:
                        self.handle_saga_failure(data, event_type)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except KeyboardInterrupt:
            pass
        finally:
            consumer.close()

    def handle_saga_success(self, data):
        """Finalize booking when all steps are successful"""
        booking_id = data.get('booking_id')
        
        with transaction.atomic():
            try:
                booking = PitchBooking.objects.get(id=booking_id)
                if booking.status == 'INITIALIZED':
                    booking.status = 'CONFIRMED'
                    booking.save()
                    self.stdout.write(self.style.SUCCESS(f" ✅ [SAGA-SUCCESS] Booking #{booking_id} has been CONFIRMED."))
            except PitchBooking.DoesNotExist:
                logger.error(f"Booking #{booking_id} not found during Saga success")

    def handle_saga_failure(self, data, event_type):
        """Mark booking as failed when any step fails"""
        booking_id = data.get('booking_id')
        reason = data.get('reason', 'Unknown error')
        
        self.stdout.write(self.style.WARNING(f" ❌ [SAGA-FAILURE] Booking #{booking_id} failed at step {event_type}. Reason: {reason}"))

        with transaction.atomic():
            try:
                booking = PitchBooking.objects.get(id=booking_id)
                if booking.status in ['INITIALIZED', 'SCHEDULED']:
                    booking.status = 'FAILED'
                    booking.save()
                    self.stdout.write(self.style.NOTICE(f" [SAGA-FAILURE] Booking #{booking_id} status set to FAILED."))
            except PitchBooking.DoesNotExist:
                logger.error(f"Booking #{booking_id} not found during Saga failure")
