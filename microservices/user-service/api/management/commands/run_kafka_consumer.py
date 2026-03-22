import json
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from confluent_kafka import Consumer, KafkaError
from api.models import User, UserOutboxEvent
from django.db import transaction

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Runs Kafka consumer for User Service to handle Saga flow'

    def handle(self, *args, **options):
        bootstrap_servers = getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        conf = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': 'user-service-saga-group',
            'auto.offset.reset': 'earliest'
        }

        consumer = Consumer(conf)
        consumer.subscribe(['pitching_events'])

        self.stdout.write(self.style.SUCCESS(f'Started Kafka Consumer for User Service'))
        
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

                    if event_type == 'startup_registration_initiated':
                        self.handle_startup_registration(data)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except KeyboardInterrupt: pass
        finally: consumer.close()

    def handle_startup_registration(self, data):
        """Update user role to founder when they register a startup"""
        user_id = data.get('user_id')
        startup_id = data.get('id')
        
        if not user_id: return

        with transaction.atomic():
            try:
                user = User.objects.get(id=user_id)
                if user.role != 'founder':
                    user.role = 'founder'
                    user.save()
                    
                    # Emit event for next step in Saga
                    UserOutboxEvent.objects.create(
                        event_type='user_role_updated',
                        payload={
                            'user_id': user.id,
                            'startup_id': startup_id,
                            'new_role': 'founder',
                            'email': user.email
                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f" [SAGA] User #{user_id} role updated to FOUNDER for Startup #{startup_id}"))
                else:
                    # Role already founder, still emit event to continue Saga
                    UserOutboxEvent.objects.create(
                        event_type='user_role_updated',
                        payload={
                            'user_id': user.id,
                            'startup_id': startup_id,
                            'new_role': 'founder',
                            'email': user.email
                        }
                    )
            except User.DoesNotExist:
                logger.error(f"User #{user_id} not found for startup registration")
