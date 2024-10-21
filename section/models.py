from django.db import models

from grade.models import Grade

# Create your models here.
class Section(models.Model):
    section = models.CharField(max_length=50)  # E.g., Grade 1, Grade 2
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='sections')

    def __str__(self):
        return f'{self.grade.grade_name} - {self.section}'
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['grade', 'section',], name='unique_grade_section')
        ]