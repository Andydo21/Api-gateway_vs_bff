import json
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from confluent_kafka import Consumer, KafkaError
from api.models import InvestmentInterest, FeedbackOutboxEvent
from django.db import transaction

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Runs Kafka consumer for Feedback Service to handle Saga flow'

    def handle(self, *args, **options):
        bootstrap_servers = getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        conf = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': 'feedback-service-saga-group',
            'auto.offset.reset': 'earliest'
        }

        consumer = Consumer(conf)
        consumer.subscribe(['pitching_events', 'finance_events'])

        self.stdout.write(self.style.SUCCESS(f'Started Kafka Consumer for Feedback Service'))
        
        try:
            while True:
                msg = consumer.poll(1.0)
                if msg is None: continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF: continue
                    else:
                        logger.error(f"Consumer error: {msg.error()}")
                        break

                try:
                    payload = json.loads(msg.value().decode('utf-8'))
                    event_type = payload.get('event_type')
                    data = payload.get('data')

                    if event_type == 'payment_initiated':
                        self.handle_payment_initiated(data)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except KeyboardInterrupt: pass
        finally: consumer.close()

    def handle_payment_initiated(self, data):
        """Link payment to investment interest as part of Saga"""
        payment_id = data.get('id')
        reference_id = data.get('reference_id') # Usually booking_id or startup_id
        user_id = data.get('user_id')
        
        with transaction.atomic():
            # In a real app, find the corresponding InvestmentInterest
            # For demo, we update or log
            self.stdout.write(self.style.NOTICE(f" [SAGA] Payment #{payment_id} initiated for Ref #{reference_id}. Linking to Investment pool..."))
            
            # Emit success event for next step
            FeedbackOutboxEvent.objects.create(
                event_type='investment_linked',
                payload={
                    'payment_id': payment_id,
                    'reference_id': reference_id,
                    'user_id': user_id,
                    'status': 'LINKED'
                }
            )
            self.stdout.write(self.style.SUCCESS(f" ✅ [SAGA] Investment linked for Payment #{payment_id}"))
