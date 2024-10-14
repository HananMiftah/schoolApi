from grade.serializers import GradeSerializer
from rest_framework import serializers
from .models import Section

class SectionSerializer(serializers.ModelSerializer):
    # school = GradeSerializer(read_only=True)  # To display school details

    class Meta:
        model = Section
        fields = '__all__'