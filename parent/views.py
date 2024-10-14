from parent.models import Parent
from parent.serializers import ParentSerializer
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
from student.models import Student
from student.serializers import StudentSerializer

class ParentViewSet(viewsets.ModelViewSet):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    permission_classes = [IsAuthenticated]  # Adjust based on your needs

    def create(self, request, *args, **kwargs):
        user = self.request.user
        
        # Ensure that the user is authenticated
        if not user.is_authenticated:
            raise PermissionDenied("You need to be authenticated to create a parent.")
                
        # Use transaction to ensure both School and Request are created together
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            parent = serializer.save()  # Save school object

            # Create corresponding request with status 'PENDING'
            # school_request = Request.objects.create(school=school, status='PENDING')
            parent.create_user_account()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['post'], url_path='upload-excel')
    def upload_parent(self, request):
        """
        Upload an Excel file and import the data into the Parent table with a school_id.
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

            # Iterate over the rows in the DataFrame and create Parent records
            for index, row in df.iterrows():
                stu_id = row.get('student_id')

                # Retrieve the student instance using the `student_id` field
                try:
                    student = Student.objects.get(student_id=stu_id)
                except Student.DoesNotExist:
                    continue  # Skip if student not found

                parent_data = {
                    'first_name': row.get('first_name'),
                    'last_name': row.get('last_name'),
                    'email': row.get('email'),
                    'phone': row.get('phone'),
                    'stu_id': row.get('student_id'),
                    'student': student.id,  # Assign the student to the parent
                    'school': school.id  # Assign the school to the parent
                }

                # Validate and create the parent instance
                serializer = ParentSerializer(data=parent_data)
                if serializer.is_valid():
                    parent = serializer.save()
                    parent.create_user_account()
                else:
                    # Log or handle the error as needed
                    continue

            return Response({"message": "Parents imported successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
