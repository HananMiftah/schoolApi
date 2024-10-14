from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.views import APIView
import pandas as pd
from rest_framework.parsers import MultiPartParser
from django.db import transaction, IntegrityError

from school.models import School
from section.models import Section
from subject.models import Subject
from teacher.models import Teacher, TeacherSectionSubject
from teacher.serializers import TeacherSectionSubjectSerializer, TeacherSerializer

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]  # Adjust based on your needs

    def create(self, request, *args, **kwargs):
        user = self.request.user
        
        # Ensure that the user is authenticated
        if not user.is_authenticated:
            raise PermissionDenied("You need to be authenticated to create a grade.")
        
        # Check if the user's role is 'school'
        if user.role != 'SCHOOL':
            raise PermissionDenied("You do not have permission to create a grade.")
        
        # Use transaction to ensure both School and Request are created together
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            teacher = serializer.save()  # Save school object

            # Create corresponding request with status 'PENDING'
            # school_request = Request.objects.create(school=school, status='PENDING')
            teacher.create_user_account()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['post'], url_path='upload-excel')
    def upload_excel(self, request):
        """
        Upload an Excel file and import the data into the Teacher table with a school_id.
        """
        file = request.FILES.get('file')
        school_id = request.data.get('school_id')  # Get the school_id from the request data
        
        if not file:
            return Response({"error": "Please upload an Excel file."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not school_id:
            return Response({"error": "Please provide a valid school_id."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the school_id exists in the School model
        try:
            school = School.objects.get(id=school_id)
        except School.DoesNotExist:
            return Response({"error": "School not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Read the Excel file into a pandas DataFrame
            df = pd.read_excel(file)

            # Iterate over the rows in the DataFrame and create Teacher records
            for index, row in df.iterrows():
                teacher_data = {
                    'first_name': row.get('first_name'),
                    'last_name': row.get('last_name'),
                    'email': row.get('email'),
                    'phone': row.get('phone'),
                    'school': school.id  # Assign the school to the teacher
                }

                # Validate and create the teacher instance
                serializer = TeacherSerializer(data=teacher_data)
                if serializer.is_valid():
                    teacher = serializer.save()
                    teacher.create_user_account()
                else:
                    # If there's a validation error, you could either log it, skip, or handle it as needed
                    continue

            return Response({"message": "Teachers imported successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='view_subject_section')
    def get_subject_and_sections(self, request, pk=None):
        teacher = self.get_object()  # Get the school instance by pk (school_id)
        subjects_sections = TeacherSectionSubject.objects.filter(teacher=teacher)  # Assuming Subject has ForeignKey to School

        if not subjects_sections.exists():
            return Response({"message": "No subjects and sections found for this teacher."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TeacherSectionSubjectSerializer(subjects_sections, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class TeacherSectionSubjectView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access this API

    def post(self, request, *args, **kwargs):
        teacher_id = request.data.get('teacher_id')
        section_id = request.data.get('section_id')
        subject_id = request.data.get('subject_id')

        # Validate the provided IDs
        try:
            teacher = Teacher.objects.get(id=teacher_id)
            section = Section.objects.get(id=section_id)
            subject = Subject.objects.get(id=subject_id)
        except (Teacher.DoesNotExist, Section.DoesNotExist, Subject.DoesNotExist) as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create or ensure the relationship is unique (based on the unique constraint)
            TeacherSectionSubject.objects.create(
                teacher=teacher, section=section, subject=subject
            )
            return Response(
                {"message": "Teacher assigned successfully."},
                status=status.HTTP_201_CREATED,
            )
        except IntegrityError:
            return Response(
                {"error": "This assignment already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def get(self, request, *args, **kwargs):
        """Retrieve all Teacher-Section-Subject assignments or a specific one by ID."""
        assignment_id = kwargs.get('pk')

        if assignment_id:
            try:
                assignment = TeacherSectionSubject.objects.get(id=assignment_id)
                serializer = TeacherSectionSubjectSerializer(assignment)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except TeacherSectionSubject.DoesNotExist:
                return Response(
                    {"error": "Assignment not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            assignments = TeacherSectionSubject.objects.all()
            serializer = TeacherSectionSubjectSerializer(assignments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        """Update an entire assignment by ID."""
        try:
            assignment = TeacherSectionSubject.objects.get(id=pk)
        except TeacherSectionSubject.DoesNotExist:
            return Response(
                {"error": "Assignment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TeacherSectionSubjectSerializer(assignment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        """Partially update an assignment by ID."""
        try:
            assignment = TeacherSectionSubject.objects.get(id=pk)
        except TeacherSectionSubject.DoesNotExist:
            return Response(
                {"error": "Assignment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TeacherSectionSubjectSerializer(
            assignment, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        """Delete an assignment by ID."""
        try:
            assignment = TeacherSectionSubject.objects.get(id=pk)
            assignment.delete()
            return Response(
                {"message": "Assignment deleted successfully."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except TeacherSectionSubject.DoesNotExist:
            return Response(
                {"error": "Assignment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )