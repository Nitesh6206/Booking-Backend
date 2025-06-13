from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .serializers import UserSerializer
import logging

# Create your views here.

logger = logging.getLogger(__name__)
class UserRegisterView(APIView):
    permission_classes = [permissions.AllowAny]  # No auth required for registration

    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"User created: {request.data.get('username')}")
                return Response({
                    "message": "User created successfully",
                    "user": serializer.data
                }, status=status.HTTP_201_CREATED)
            logger.warning(f"User creation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

