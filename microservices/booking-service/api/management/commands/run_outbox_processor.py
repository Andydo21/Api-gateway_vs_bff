import time
import json
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import BookingOutboxEvent
from api.kafka_producer import producer

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Polls BookingOutboxEvent table and sends events to Kafka'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Started Outbox Processor for Booking Service'))
        
        while True:
            try:
                # Get unprocessed events
                events = BookingOutboxEvent.objects.filter(processed=False).order_by('created_at')[:100]
                
                if not events:
                    time.sleep(1)  # Wait if no events
                    continue

                for event in events:
                    self.stdout.write(f"Processing event {event.id}: {event.event_type}")
                    
                    # Publish to Kafka
                    producer.publish_event(
                        topic='pitching_events',
                        event_type=event.event_type,
                        data=event.payload
                    )
                    
                    # Mark as processed
                    event.processed = True
                    event.processed_at = timezone.now()
                    event.save()
                    
                    self.stdout.write(self.style.SUCCESS(f"Successfully processed event {event.id}"))

            except Exception as e:
                logger.error(f"Error in Outbox Processor: {e}")
                self.stdout.write(self.style.ERROR(f"Error: {e}"))
                time.sleep(5)
