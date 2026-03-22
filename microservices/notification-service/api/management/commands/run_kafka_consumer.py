import json
import logging
import asyncio
from django.core.management.base import BaseCommand
from django.conf import settings
from confluent_kafka import Consumer, KafkaError
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Runs Kafka consumer for Notification Service'

    def handle(self, *args, **options):
        bootstrap_servers = getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        conf = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': 'notification-service-group',
            'auto.offset.reset': 'earliest'
        }

        consumer = Consumer(conf)
        consumer.subscribe(['pitching_events', 'finance_events', 'identity_events'])

        self.stdout.write(self.style.SUCCESS(f'Started Kafka Consumer for Notification Service (Brokers: {bootstrap_servers})'))
        
        channel_layer = get_channel_layer()

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
                        self.process_pitch_booking_created(data)
                    elif event_type == 'startup_created':
                        self.process_startup_created(data)
                    elif event_type == 'payment_completed':
                        self.process_payment_completed(data)
                    elif event_type == 'payment_failed':
                        self.process_payment_failed(data)
                    elif event_type == 'interaction_tracked':
                        self.process_interaction_tracked(data)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except KeyboardInterrupt:
            pass
        finally:
            consumer.close()

    def process_startup_created(self, startup_data):
        # Implementation for startup_created notification
        pass

    def process_payment_completed(self, payment_data):
        user_id = payment_data.get('user_id')
        self._send_socket_notification(user_id, {
            'type': 'notification_message',
            'message': f'Thanh toán thành công cho Reference #{payment_data.get("reference_id")}!',
            'notification_type': 'success'
        })

    def process_payment_failed(self, payment_data):
        user_id = payment_data.get('user_id')
        self._send_socket_notification(user_id, {
            'type': 'notification_message',
            'message': f'Thanh toán thất bại: {payment_data.get("error_message")}',
            'notification_type': 'error'
        })

    def process_interaction_tracked(self, interaction_data):
        # Logic for interaction notification (e.g. to admin or startup owner)
        pass

    def _send_socket_notification(self, user_id, message):
        if not user_id: return
        group_name = f'user_{user_id}'
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(group_name, message)

    def process_pitch_booking_created(self, booking_data):
        """Handle pitch_booking_created event by pushing to WebSockets"""
        user_id = booking_data.get('user_id')
        booking_id = booking_data.get('id')
        
        if not user_id:
            return

        group_name = f'user_{user_id}'
        message = {
            'type': 'notification_message',
            'message': f'Hệ thống: Pitch Booking #{booking_id} của bạn đã được xác nhận (via Kafka)!',
            'notification_type': 'success',
            'booking_id': booking_id
        }

        self.stdout.write(self.style.NOTICE(f" [KAFKA] Booking #{booking_id} ➔ Pushing to WebSocket group: {group_name}"))

        # Push to Channels group
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_name,
            message
        )
