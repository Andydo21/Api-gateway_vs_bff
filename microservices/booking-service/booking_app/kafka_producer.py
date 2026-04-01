import json
import logging
from confluent_kafka import Producer
from django.conf import settings

logger = logging.getLogger(__name__)

class KafkaProducer:
    def __init__(self):
        self.bootstrap_servers = getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.conf = {
            'bootstrap.servers': self.bootstrap_servers,
            'client.id': 'booking-service-producer',
            'enable.idempotence': True,
            'acks': 'all',
            'retries': 5
        }
        try:
            self.producer = Producer(self.conf)
        except Exception as e:
            logger.error(f"Failed to create Kafka producer: {e}")
            self.producer = None

    def delivery_report(self, err, msg):
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    def publish_event(self, topic, event_type, data, message_id=None):
        if not self.producer:
            logger.warning("Kafka producer not initialized. Skipping event.")
            return

        message = {
            'event_type': event_type,
            'message_id': message_id,
            'data': data
        }
        
        try:
            self.producer.produce(
                topic, 
                key=str(data.get('order_id', '')),
                value=json.dumps(message).encode('utf-8'),
                callback=self.delivery_report
            )
            # Use flush() with a timeout to ensure reliable delivery
            # while preventing the application from hanging indefinitely
            self.producer.flush(timeout=5.0)
            logger.info(f"Published {event_type} to {topic} (Confirmed)")
        except Exception as e:
            logger.error(f"Error publishing to Kafka: {e}")

# Global instance
producer = KafkaProducer()

def publish_pitch_booking_created(booking_data):
    producer.publish_event('pitching_events', 'pitch_booking_created', booking_data)
