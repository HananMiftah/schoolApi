from django.db import models
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import random
import string

from users.models import User

class School(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name
    
    def generate_username(self):
        # Generate a unique username based on the school name
        username = self.name.replace(" ", "_").lower()
        suffix = random.randint(1, 9999)
        return f"{username}_{suffix}"

    def generate_password(self, length=10):
        # Generate a random password
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))
    def send_credentials_via_email(self,username,password):
        subject = 'Your School Account Credentials'
        message = f'Hello {self.name},\n\nYour account has been created successfully.\n\nUsername: {username}\nPassword: {password}\n\nPlease keep your credentials safe.'
        recipient_list = [self.email]

        # Send the email
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

    def create_user_account(self):
        # Generate a username and password
        username = self.generate_username()
        password = self.generate_password()

        # Create a user in the User model
        user, created = User.objects.get_or_create(
            username=username,
            email=self.email,
            role='SCHOOL'
        )

        # If the user was newly created, set the password and save
        if created:
            user.set_password(password)  # This hashes the password
        else:
            user.set_password(password)  # Even if the user exists, re-hash the password
        
        # Save the user with the hashed password
        user.save()

        # Send credentials via email
        self.send_credentials_via_email(username,password)

        # Save the school instance with the generated username and password
        self.save()