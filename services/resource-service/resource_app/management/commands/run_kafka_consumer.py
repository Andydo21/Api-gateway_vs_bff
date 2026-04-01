import json
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from confluent_kafka import Consumer, KafkaError
from resource_app.models import EventResource, ResourceReservation
from django.utils import timezone

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Runs Kafka consumer for Pitching Hub Resources'

    def handle(self, *args, **options):
        bootstrap_servers = getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        conf = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': 'resource-service-group',
            'auto.offset.reset': 'earliest'
        }

        consumer = Consumer(conf)
        consumer.subscribe(['pitching_events'])

        self.stdout.write(self.style.SUCCESS(f'Started Kafka Consumer for Resource Service (Brokers: {bootstrap_servers})'))

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

                    if event_type == 'pitch_booking_created':
                        self.process_booking_created(data)
                    elif event_type == 'pitch_booking_cancelled':
                        self.process_booking_cancelled(data)
                    elif event_type == 'startup_created':
                        self.process_startup_created(data)
                    elif event_type == 'startup_deleted':
                        self.process_startup_deleted(data)
                    elif event_type == 'startup_updated':
                        self.process_startup_updated(data)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except KeyboardInterrupt:
            pass
        finally:
            consumer.close()

    def process_booking_created(self, booking_data):
        """Handle pitch_booking_created event by updating resource reservations"""
        # This can be used to automatically fulfill/confirm reservations
        booking_id = booking_data.get('id')
        items = booking_data.get('resource_items', []) # Assuming booking includes resources
        
        self.stdout.write(self.style.NOTICE(f" [KAFKA] Processing Booking #{booking_id} Confirmation"))
        
        # In this domain, we might automatically confirm active reservations
        reservations = ResourceReservation.objects.filter(booking_id=booking_id, status='active')
        for res in reservations:
            res.status = 'fulfilled'
            res.save()
            
            # Reduce actual available quantity if not already done during reservation
            # (Usually done during reservation, but we ensure here)
            self.stdout.write(self.style.SUCCESS(f"   ✅ Fulfilled reservation for Booking {booking_id}"))

    def process_booking_cancelled(self, booking_data):
        """Handle pitch_booking_cancelled event by releasing resources"""
        booking_id = booking_data.get('booking_id')
        
        self.stdout.write(self.style.NOTICE(f" [KAFKA] Releasing resources for Cancelled Booking #{booking_id}"))
        
        reservations = ResourceReservation.objects.filter(booking_id=booking_id, status='active')
        for res in reservations:
            resource = res.resource
            resource.available_quantity += res.quantity
            resource.reserved_quantity -= res.quantity
            resource.save()
            
            res.status = 'released'
            res.save()
            self.stdout.write(self.style.SUCCESS(f"   ✅ Released resources for Booking {booking_id}"))

    def process_startup_created(self, startup_data):
        """Handle startup_created event by initializing resource record"""
        startup_id = startup_data.get('id')
        startup_name = startup_data.get('company_name', 'Unknown Startup')
        
        self.stdout.write(self.style.NOTICE(f" [KAFKA] Initializing resources for New Startup #{startup_id}: {startup_name}"))
        
        resource, created = EventResource.objects.get_or_create(
            startup_id=startup_id,
            defaults={
                'startup_name': startup_name,
                'available_quantity': 5, # Default demo booths
                'reserved_quantity': 0
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"   ✅ Created new resource record for Startup {startup_id}"))
        else:
            self.stdout.write(self.style.WARNING(f"   ⚠️ Resource record already exists for Startup {startup_id}"))

    def process_startup_deleted(self, startup_data):
        """Handle startup_deleted event by removing resource record"""
        startup_id = startup_data.get('id')
        
        self.stdout.write(self.style.NOTICE(f" [KAFKA] Removing resources for Deleted Startup #{startup_id}"))
        
        try:
            resource = EventResource.objects.get(startup_id=startup_id)
            resource.delete()
            self.stdout.write(self.style.SUCCESS(f"   ✅ Deleted resource record for Startup {startup_id}"))
        except EventResource.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"   ⚠️ Resource record for Startup {startup_id} not found"))

    def process_startup_updated(self, startup_data):
        """Handle startup_updated event by updating resource metadata"""
        startup_id = startup_data.get('id')
        startup_name = startup_data.get('company_name')
        
        self.stdout.write(self.style.NOTICE(f" [KAFKA] Updating resource metadata for Startup #{startup_id}: {startup_name}"))
        
        try:
            resource = EventResource.objects.get(startup_id=startup_id)
            resource.startup_name = startup_name
            resource.save()
            self.stdout.write(self.style.SUCCESS(f"   ✅ Updated resource record for Startup {startup_id}"))
        except EventResource.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"   ⚠️ Resource record for Startup {startup_id} not found"))
