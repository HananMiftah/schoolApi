from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from section.models import Section
from section.serializers import SectionSerializer
from teacher.models import TeacherSectionSubject
from teacher.serializers import TeacherSectionSubjectSerializer


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
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

    @action(detail=True, methods=['get'], url_path='view_teacher_subject')
    def get_subject_and_teachers(self, request, pk=None):
        try:
            # Retrieve the section by primary key (pk)
            section = self.get_object()

            # Query TeacherSectionSubject relationships for the given section
            subjects_teachers = TeacherSectionSubject.objects.filter(section=section)

            if not subjects_teachers.exists():
                return Response(
                    {"message": "No subjects and teachers found for this section."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Prepare a response with only serializable fields
            response_data = [
                {
                    "teacher": st.teacher.first_name,
                    "subject": st.subject.subject,
                }
                for st in subjects_teachers
            ]

            return Response(response_data, status=status.HTTP_200_OK)

        except Section.DoesNotExist:
            return Response(
                {"error": "Section not found."}, status=status.HTTP_404_NOT_FOUND
            )