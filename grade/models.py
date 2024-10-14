from django.db import models

from school.models import School

# Create your models here.
class Grade(models.Model):
    grade_name = models.CharField(max_length=50)  # E.g., Grade 1, Grade 2
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='grades')

    def __str__(self):
        return f'{self.grade_name} - {self.school.name}'