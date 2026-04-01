from rest_framework import serializers
from .models import Feedback, InvestmentInterest

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

class InvestmentInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentInterest
        fields = '__all__'
