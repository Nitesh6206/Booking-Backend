from rest_framework import serializers
from .models import PersonalizedFitnessPlan

class FitnessPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalizedFitnessPlan
        fields = '__all__'
        read_only_fields = ('created_at',)