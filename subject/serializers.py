from rest_framework import serializers
from subject.models import Subject

class SubjectSerializer(serializers.ModelSerializer):
    # school = SchoolSerializer(read_only=True)  # To display school details

    class Meta:
        model = Subject
        fields = '__all__'