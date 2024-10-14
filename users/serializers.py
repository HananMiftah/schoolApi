# users/serializers.py
from rest_framework import serializers

from .models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'role']

    def create(self, validated_data):
        # Create the user and hash the password
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role']
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
                
                # This will hash the input password and compare it to the stored hash
                if not user.check_password(password):
                    raise serializers.ValidationError("Incorrect password or password")
                    
            except User.DoesNotExist:
                raise serializers.ValidationError("User does not exist")
        else:
            raise serializers.ValidationError("Email and password are required")

        data['user'] = user
        return data
