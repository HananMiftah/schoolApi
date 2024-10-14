from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action

from school.models import School
from section.models import Section
from student.models import Student
from student.serializers import StudentSerializer
import pandas as pd
from rest_framework.parsers import MultiPartParser
from django.db import transaction, IntegrityError

from teacher.models import TeacherSectionSubject
from teacher.serializers import TeacherSectionSubjectSerializer

# Create your views here.
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]  # Adjust based on your needs

    @action(detail=False, methods=['post'], url_path='upload-excel')
    def upload_excel(self, request):
        """
        Upload an Excel file and import the data into the Teacher table with a school_id.
        """
        file = request.FILES.get('file')
        school_id = request.data.get('school_id')
        section_id = request.data.get('section_id')  # Get the school_id from the request data
        
        if not file:
            return Response({"error": "Please upload an Excel file."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not school_id or not section_id:
            return Response({"error": "Please provide a valid school_id or section_id."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the school_id exists in the School model
        try:
            school = School.objects.get(id=school_id)
            section = Section.objects.get(id=section_id)

        except (School.DoesNotExist, Section.DoesnotExist):
            return Response({"error": "School or Section not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Read the Excel file into a pandas DataFrame
            df = pd.read_excel(file)

            # Iterate over the rows in the DataFrame and create Teacher records
            for index, row in df.iterrows():
                student_data = {
                    'first_name': row.get('first_name'),
                    'last_name': row.get('last_name'),
                    'student_id': row.get('student_id'),
                    'section': section_id,
                    'age': row.get('age'),
                    'gender': row.get('gender'),
                    'school': school_id  # Assign the school to the teacher
                }

                # Validate and create the teacher instance
                serializer = StudentSerializer(data=student_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    # If there's a validation error, you could either log it, skip, or handle it as needed
                    continue

            return Response({"message": "Students imported successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], url_path='get-teacher-subject')
    def get_teacher_subject(self, request, pk=None):

        student = self.get_object()
        section = student.section 
        subjects_teachers = TeacherSectionSubject.objects.filter(section=section) 

        if not subjects_teachers.exists():
            return Response({"message": "No subject and teacher found for this student."}, status=status.HTTP_404_NOT_FOUND)
        
        response_data = [
                {
                    "teacher": st.teacher.first_name,
                    "subject": st.subject.subject,
                }
                for st in subjects_teachers
            ]

        return Response(response_data, status=status.HTTP_200_OK)
