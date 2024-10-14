from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Request, School
from .serializers import RequestSerializer
from django.db import transaction
from django.core.mail import send_mail  # For sending email
from django.conf import settings  # To access email configurations

class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

    @action(detail=True, methods=['put'], url_path='approve')
    def approve_request(self, request, pk=None):
        try:
            school_request = self.get_object()  # Get the request object
            if school_request.status == 'APPROVED':
                return Response({'error': 'Request is already approved.'}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                # Approve the request
                school_request.status = 'APPROVED'
                school_request.save()

                # Generate username and password for the associated school
                school = school_request.school
                # If needed, generate username and password
                # school.username = school.generate_username()
                # school.password = school.generate_password()
                
                school.save()

                # Send the credentials via email
                school.create_user_account()

            return Response({'message': 'School request approved successfully!'}, status=status.HTTP_200_OK)

        except Request.DoesNotExist:
            return Response({'error': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['put'], url_path='cancel')
    def cancel_request(self, request, pk=None):
        try:
            school_request = self.get_object()  # Get the request object
            if school_request.status == 'CANCELED':
                return Response({'error': 'Request is already canceled.'}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                # Cancel the request
                school_request.status = 'CANCELED'
                school_request.save()

                # Send a cancellation email to the school
                school = school_request.school
                self.send_cancellation_email(school)

            return Response({'message': 'School request canceled successfully!'}, status=status.HTTP_200_OK)

        except Request.DoesNotExist:
            return Response({'error': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)

    def send_cancellation_email(self, school):
        # Use Django's send_mail function to send an email
        send_mail(
            subject='Registration Canceled',
            message=f'Dear {school.name},\n\nYour school registration has been canceled. If you have any questions, feel free to contact us.\n\nBest regards,\nThe Team',
            from_email=settings.DEFAULT_FROM_EMAIL,  # Make sure this is set in your settings.py
            recipient_list=[school.email],  # Send the email to the school's email address
            fail_silently=False,
        )
