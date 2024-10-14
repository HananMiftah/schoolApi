from django.db import models
from section.models import Section  # Assuming Section model is in section app
from school.models import School   # Assuming School model is in school app

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)  # ID given by the school
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=50)
    
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='students')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='students')

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.school.name}'

    class Meta:
        unique_together = ('student_id', 'school')  # Ensure uniqueness across the school
