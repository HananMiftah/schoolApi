from django.db import models

from school.models import School

# Create your models here.
class Subject(models.Model):
    subject = models.CharField(max_length=255)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='sections')

    def __str__(self):
        return f'{self.subject} - {self.school.name}'