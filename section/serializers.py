from rest_framework import serializers
from .models import Section

class SectionSerializer(serializers.ModelSerializer):
    grade_name = serializers.CharField(source='grade.grade_name', read_only=True)  # Custom field

    class Meta:
        model = Section
        fields = ['id', 'section', 'grade', 'grade_name']  # Include both grade_name and grade if needed
