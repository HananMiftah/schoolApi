# users/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer,LoginSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # Custom action for deleting all users
    @action(detail=False, methods=['delete'], url_path='delete-all')
    def delete_all(self, request):
        # Perform bulk deletion of all user records
        User.objects.all().delete()
        return Response({"message": "All users have been deleted."}, status=status.HTTP_204_NO_CONTENT)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                      'email': user.email,
                    'role': user.role,  # Assuming you have a 'role' field
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)  # Only authenticated users can log out

    def post(self, request):
        try:
            # Get the refresh token from the request data
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            
            # Blacklist the refresh token
            token.blacklist()

            return Response({"message": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
