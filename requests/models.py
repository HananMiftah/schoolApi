from django.db import models
from school.models import School

class Request(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)  # Relate request to school
    STATUS_CHOICES = [
        ('PENDING', 'PENDING'),
        ('APPROVED', 'APPROVED'),
        ('CANCELLED', 'CANCELLED'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"Request {self.id} for School {self.school.name} - Status: {self.status}"

    def approve(self):
        # When a request is approved, generate credentials for the school and create a user account
        if self.status == 'APPROVED':
            self.school.create_user_account()  # Calls the school method to create the user account
