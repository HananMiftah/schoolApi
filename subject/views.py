from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from subject.models import Subject
from subject.serializers import SubjectSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]  # Ensures the user is authenticated

    def perform_create(self, serializer):
        user = self.request.user
        
        # Ensure that the user is authenticated
        if not user.is_authenticated:
            raise PermissionDenied("You need to be authenticated to create a grade.")
        
        # Check if the user's role is 'school'
        if user.role != 'SCHOOL':
            raise PermissionDenied("You do not have permission to create a grade.")
        
        # If the user's role is 'school', proceed with saving the grade
        serializer.save()
