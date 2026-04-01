import json
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from confluent_kafka import Consumer, KafkaError
from user_app.models import User, UserOutboxEvent, ProcessedMessage
from django.db import transaction, IntegrityError

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

                        if event_type == 'pitch_booking_created':
                            self.process_pitch_booking_created(data)
                        elif event_type == 'startup_created':
                            self.process_startup_created(data)
                        elif event_type == 'user_role_updated':
                            self.process_user_role_updated(data)
                        elif event_type == 'investment_linked':
                            self.process_investment_linked(data)
                        elif event_type == 'payment_completed':
                            self.process_payment_completed(data)
                        elif event_type == 'payment_failed':
                            self.process_payment_failed(data)
                        elif event_type == 'interaction_tracked':
                            self.process_interaction_tracked(data)
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
