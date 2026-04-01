import json
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from confluent_kafka import Consumer, KafkaError
from startup_app.models import Startup, StartupOutboxEvent, ProcessedMessage
from django.db import transaction, IntegrityError

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Runs Kafka consumer for Startup Service to handle Saga flow'

    def handle(self, *args, **options):
        bootstrap_servers = getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        conf = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': 'startup-service-saga-group',
            'auto.offset.reset': 'earliest'
        }

        consumer = Consumer(conf)
        consumer.subscribe(['pitching_events'])

        self.stdout.write(self.style.SUCCESS(f'Started Kafka Consumer for Startup Service'))
        
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
                    message_id = payload.get('message_id')
                    data = payload.get('data')

                    if message_id:
                        if ProcessedMessage.objects.filter(message_id=message_id).exists():
                            self.stdout.write(f"Skipping already processed message: {message_id}")
                            continue

                    with transaction.atomic():
                        # Save message_id to prevent re-processing
                        if message_id:
                            try:
                                ProcessedMessage.objects.create(message_id=message_id)
                            except IntegrityError:
                                self.stdout.write(f"Skipping already processed message: {message_id}")
                                continue

                        if event_type == 'welcome_email_sent':
                            self.handle_registration_success(data)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except KeyboardInterrupt: pass
        finally: consumer.close()

    def handle_registration_success(self, data):
        """Finalize startup registration Saga"""
        startup_id = data.get('startup_id')
        self.stdout.write(self.style.SUCCESS(f" [SAGA-SUCCESS] Registration flow completed for Startup #{startup_id}"))
        # More logic could go here if needed
