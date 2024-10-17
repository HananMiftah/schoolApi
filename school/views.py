from django.http import Http404
from django.shortcuts import get_object_or_404
from grade.models import Grade
from grade.serializers import GradeSerializer
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction

from section.models import Section
from section.serializers import SectionSerializer
from student.models import Student
from student.serializers import StudentSerializer
from subject.models import Subject
from subject.serializers import SubjectSerializer
from teacher.models import Teacher
from teacher.serializers import TeacherSerializer
from users.models import User
from .models import School
from .serializers import SchoolSerializer
from requests.models import Request  # Assuming this is your Request model

class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [AllowAny]  # Adjust based on your needs

    def create(self, request, *args, **kwargs):
        # Use transaction to ensure both School and Request are created together
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            school = serializer.save()  # Save school object

            # Create corresponding request with status 'PENDING'
            school_request = Request.objects.create(school=school, status='PENDING')

            headers = self.get_success_headers(serializer.data)
            return Response({
                'message': 'School registration submitted successfully!',
                'school_id': school.id,
                'request_id': school_request.id
            }, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        # Override destroy method to delete school, related user and request
        school = self.get_object()  # Get the school instance

        with transaction.atomic():
            # Find and delete the associated user by the school's email
            try:
                user = User.objects.get(email=school.email)
                user.delete()  # Delete the corresponding user
            except User.DoesNotExist:
                pass  # If no user is found, continue

            # Delete related requests
            Request.objects.filter(school=school).delete()

            # Delete the school itself
            school.delete()

        return Response({"message": "School and related records have been deleted."}, status=status.HTTP_204_NO_CONTENT)
    # Add a custom action to retrieve a school by email
    @action(detail=False, methods=['get'], url_path='email=(?P<email>.+)')
    def get_school_by_email(self, request, email=None):
        print(f"Received email: {email}")  # Print the email for debugging

        try:
            school = School.objects.get(email=email)
            serializer = self.get_serializer(school)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except School.DoesNotExist:
            print("School not found")  # Debug print
            raise Http404("School not found")
    
    @action(detail=False, methods=['delete'], url_path='delete-all')
    def delete_all(self, request):
        # Perform bulk deletion of all school records and related users and requests
        with transaction.atomic():
            for school in School.objects.all():
                # Find and delete the associated user by the school's email
                try:
                    user = User.objects.get(email=school.email)
                    user.delete()  # Delete the corresponding user
                except User.DoesNotExist:
                    pass  # If no user is found, continue

                # Delete related requests
                Request.objects.filter(school=school).delete()

            # Delete all schools
            School.objects.all().delete()

        return Response({"message": "All schools and related records have been deleted."}, status=status.HTTP_204_NO_CONTENT)
    @action(detail=True, methods=['get'], url_path='get-grades')
    def get_grades(self, request, pk=None):
        school = self.get_object()  # Get the school instance by pk (school_id)
        grades = Grade.objects.filter(school=school)  # Assuming Grade has ForeignKey to School

        if not grades.exists():
            return Response({"message": "No grades found for this school."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = GradeSerializer(grades, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Additional action to delete all grades for a specific school
    @action(detail=True, methods=['delete'], url_path='delete-grades')
    def delete_grades(self, request, pk=None):
        school = self.get_object()  # Get the school instance
        grades = Grade.objects.filter(school=school)  # Assuming Grade has a ForeignKey to School
        
        if not grades.exists():
            return Response({"message": "No grades found to delete for this school."}, status=status.HTTP_404_NOT_FOUND)
        
        grades.delete()  # Delete all grades for this school
        return Response({"message": "All grades for the school have been deleted."}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='get-school-sections')
    def get_school_sections(self, request, pk=None):
        school = self.get_object()  # Get the school instance by pk (school_id)
        grades = Grade.objects.filter(school=school)  # Assuming Grade has ForeignKey to School
        
        if not grades.exists():
            return Response({"message": "No grades found for this school."}, status=status.HTTP_404_NOT_FOUND)

        # Filter sections where the grade is in the grades queryset
        sections = Section.objects.filter(grade__in=grades)

        if not sections.exists():
            return Response({"message": "No sections found for this school."}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the sections
        serializer = SectionSerializer(sections, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['delete'], url_path='delete-school-sections')
    def delete_school_sections(self, request, pk=None):
        school = self.get_object()  # Get the school instance by pk (school_id)
        grades = Grade.objects.filter(school=school)  # Assuming Grade has ForeignKey to School
        
        if not grades.exists():
            return Response({"message": "No grades found for this school."}, status=status.HTTP_404_NOT_FOUND)

        # Filter sections where the grade is in the grades queryset
        sections = Section.objects.filter(grade__in=grades)

        if not sections.exists():
            return Response({"message": "No sections found for this school."}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the sections
        sections.delete()  # Delete all grades for this school
        return Response({"message": "All sections for the school have been deleted."}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='get-subjects')
    def get_subjects(self, request, pk=None):
        school = self.get_object()  # Get the school instance by pk (school_id)
        subjects = Subject.objects.filter(school=school)  # Assuming Subject has ForeignKey to School

        if not subjects.exists():
            return Response({"message": "No subjects found for this school."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Additional action to delete all grades for a specific school
    @action(detail=True, methods=['delete'], url_path='delete-subjects')
    def delete_subjects(self, request, pk=None):
        school = self.get_object()  # Get the school instance
        subjects = Subject.objects.filter(school=school)  # Assuming Grade has a ForeignKey to School
        
        if not subjects.exists():
            return Response({"message": "No subject found to delete for this school."}, status=status.HTTP_404_NOT_FOUND)
        
        subjects.delete()  # Delete all grades for this school
        return Response({"message": "All subjects for the school have been deleted."}, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'], url_path='get-teachers')
    def get_teachers(self, request, pk=None):
        user = self.request.user
        
        # Ensure that the user is authenticated
        if not user.is_authenticated:
            raise PermissionDenied("You need to be authenticated to create a grade.")
        
        # Check if the user's role is 'school'
        if user.role != 'SCHOOL':
            raise PermissionDenied("You do not have permission to create a grade.")
        school = self.get_object()  # Get the school instance by pk (school_id)
        teachers = Teacher.objects.filter(school=school)  # Assuming Subject has ForeignKey to School

        if not teachers.exists():
            return Response({"message": "No teachers found for this school."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TeacherSerializer(teachers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Additional action to delete all grades for a specific school
    @action(detail=True, methods=['delete'], url_path='delete-teachers')
    def delete_teachers(self, request, pk=None):
        user = self.request.user
        
        # Ensure that the user is authenticated
        if not user.is_authenticated:
            raise PermissionDenied("You need to be authenticated to create a grade.")
        
        # Check if the user's role is 'school'
        if user.role != 'SCHOOL':
            raise PermissionDenied("You do not have permission to create a grade.")
        school = self.get_object()  # Get the school instance
        teachers = Teacher.objects.filter(school=school) 
        
        if not teachers.exists():
            return Response({"message": "No teachers found to delete for this school."}, status=status.HTTP_404_NOT_FOUND)
        
        teachers.delete()  # Delete all grades for this school
        return Response({"message": "All teachers for the school have been deleted."}, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'], url_path='get-students')
    def get_students(self, request, pk=None):
        user = self.request.user
        
        # Ensure that the user is authenticated
        if not user.is_authenticated:
            raise PermissionDenied("You need to be authenticated to view students.")
        
        school = self.get_object()  # Get the school instance by pk (school_id)
        students = Student.objects.filter(school=school) 

        if not students.exists():
            return Response({"message": "No students found for this school."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Additional action to delete all grades for a specific school
    @action(detail=True, methods=['delete'], url_path='delete-students')
    def delete_students(self, request, pk=None):
        user = self.request.user
        
        # Ensure that the user is authenticated
        if not user.is_authenticated:
            raise PermissionDenied("You need to be authenticated to delete students.")
        
        school = self.get_object()  # Get the school instance
        students = Student.objects.filter(school=school) 
        
        if not students.exists():
            return Response({"message": "No students found to delete for this school."}, status=status.HTTP_404_NOT_FOUND)
        
        students.delete()  # Delete all grades for this school
        return Response({"message": "All students for the school have been deleted."}, status=status.HTTP_204_NO_CONTENT)