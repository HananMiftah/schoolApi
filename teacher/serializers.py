# school/serializers.py
from rest_framework import serializers
from .models import Teacher, TeacherSectionSubject

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'first_name', 'last_name', 'phone', 'email','school'] 

class TeacherSectionSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherSectionSubject
        fields = "__all__"
