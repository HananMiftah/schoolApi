from rest_framework import serializers
from school.serializers import SchoolSerializer
from .models import Grade

class GradeSerializer(serializers.ModelSerializer):
    # school = SchoolSerializer(read_only=True)  # To display school details

    class Meta:
        model = Grade
        fields = '__all__'