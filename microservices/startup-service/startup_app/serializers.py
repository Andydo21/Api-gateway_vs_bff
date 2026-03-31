"""Product Service Serializers"""
from rest_framework import serializers
from .models import Startup, Category, Review, Investor


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'startup', 'user_id', 'username', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']


class StartupSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Startup
        fields = ['id', 'user_id', 'company_name', 'description', 'industry', 'website', 
                  'category', 'category_name', 'image_url', 'featured', 
                  'funding_stage', 'funding_goal', 'team_size', 'location',
                  'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class InvestorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investor
        fields = ['id', 'user_id', 'company_name', 'bio', 'interests', 'created_at']
        read_only_fields = ['id', 'created_at']



class StartupDetailSerializer(StartupSerializer):

    reviews_count = serializers.SerializerMethodField()
    
    class Meta(StartupSerializer.Meta):
        fields = StartupSerializer.Meta.fields + ['reviews_count']
    
    def get_reviews_count(self, obj):
        return obj.reviews.count()
