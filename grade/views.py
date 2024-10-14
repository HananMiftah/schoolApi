from rest_framework import viewsets,status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action


from grade.models import Grade
from grade.serializers import GradeSerializer
from section.models import Section
from section.serializers import SectionSerializer

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
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
    
    @action(detail=True, methods=['get'], url_path='get-sections')
    def get_sections(self, request, pk=None):
        user = self.request.user
        
        # Ensure that the user is authenticated
        if not user.is_authenticated:
            raise PermissionDenied("You need to be authenticated to view grades.")
        
        # Check if the user's role is 'school'
        if user.role != 'SCHOOL':
            raise PermissionDenied("You do not have permission to view grades.")

        grade = self.get_object()
        sections = Section.objects.filter(grade=grade)  # Assuming Grade has ForeignKey to School

        if not sections.exists():
            return Response({"message": "No section found for this grade."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SectionSerializer(sections, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='delete-sections')
    def delete_sections(self, request, pk=None):
        user = self.request.user
        
        # Ensure that the user is authenticated
        if not user.is_authenticated:
            raise PermissionDenied("You need to be authenticated to delete grades.")
        
        # Check if the user's role is 'school'
        if user.role != 'SCHOOL':
            raise PermissionDenied("You do not have permission to delete grades.")

        grade = self.get_object()
        sections = Section.objects.filter(grade=grade)

        if not sections.exists():
            return Response({"message": "No section found for this grade."}, status=status.HTTP_404_NOT_FOUND)
        
        sections.delete()
        return Response({"message": "All sections for the school have been deleted."}, status=status.HTTP_204_NO_CONTENT)
