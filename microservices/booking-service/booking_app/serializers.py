from rest_framework import serializers
from .models import PitchRequest, PitchBooking, Waitlist, PitchBookingHistory

class PitchRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PitchRequest
        fields = '__all__'

class PitchBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PitchBooking
        fields = '__all__'

class CreateBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PitchBooking
        fields = ['pitch_request', 'pitch_slot_id']

class WaitlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waitlist
        fields = '__all__'

class PitchBookingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PitchBookingHistory
        fields = '__all__'
