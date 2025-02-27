from django.contrib.auth.models import User
from rest_framework import serializers

class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'validators': []},  
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists.')
        return value

