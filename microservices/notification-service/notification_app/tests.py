from django.test import TestCase, Client
from django.urls import reverse
from .models import Notification
from .serializers import NotificationSerializer
import json

class NotificationModelTest(TestCase):
    def test_notification_creation(self):
        notif = Notification.objects.create(
            user_id=1,
            message="Test",
            notification_type="info"
        )
        self.assertEqual(notif.message, "Test")
        self.assertFalse(notif.is_read)
        self.assertIsNotNone(notif.created_at)

class NotificationSerializerTest(TestCase):
    def test_serializer_output(self):
        notif = Notification.objects.create(
            user_id=1,
            message="Test",
            notification_type="info"
        )
        serializer = NotificationSerializer(notif)
        self.assertEqual(serializer.data['message'], "Test")
        self.assertEqual(serializer.data['user_id'], 1)

class NotificationAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_id = 1
        self.notif_data = {
            'user_id': self.user_id,
            'message': 'Test message',
            'notification_type': 'success'
        }

    def test_send_notification(self):
        """Test the send endpoint logic"""
        # Mock channel layer if needed, but for simple logic test, checking DB is enough
        response = self.client.post(
            '/api/send/',
            data=json.dumps(self.notif_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(Notification.objects.first().message, 'Test message')

    def test_list_notifications(self):
        """Test the list endpoint query"""
        Notification.objects.create(**self.notif_data)
        response = self.client.get(f'/api/list/?user_id={self.user_id}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']), 1)

    def test_mark_as_read(self):
        """Test marking a notification as read"""
        notif = Notification.objects.create(**self.notif_data)
        response = self.client.put(f'/api/{notif.id}/read/')
        self.assertEqual(response.status_code, 200)
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)
