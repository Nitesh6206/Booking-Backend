"""
API views for managing fitness classes and bookings.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import transaction
from .models import FitnessClass, Booking
from .serializers import FitnessClassSerializer, BookingSerializer
import logging
import pytz

logger = logging.getLogger(__name__)

class FitnessClassView(APIView):
    """Handles CRUD operations for fitness classes."""

    def get(self, request):
        """Retrieve upcoming fitness classes with optional timezone filtering."""
        try:
            timezone_name = request.query_params.get('timezone', 'Asia/Kolkata')
            fitnessclass_type= request.query_params.get('fitnessclass_type', None)
            try:
                user_timezone = pytz.timezone(timezone_name)
            except pytz.exceptions.UnknownTimeZoneError:
                logger.warning(f"Invalid timezone provided: {timezone_name}")
                return Response(
                    {"error": "Invalid timezone"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            classes = FitnessClass.objects.filter(date_time__gt=timezone.now()).order_by('date_time')
            if fitnessclass_type is not None:
                classes = classes.filter(name=fitnessclass_type)
            serializer = FitnessClassSerializer(classes, many=True, context={'timezone': user_timezone})
            logger.info(f"Retrieved {len(classes)} classes for timezone {timezone_name}")
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Error retrieving classes: {str(e)}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """Create a new fitness class."""
        try:
            serializer = FitnessClassSerializer(data=request.data)
            if serializer.is_valid():
                with transaction.atomic():
                    serializer.save()
                    logger.info(f"Created fitness class: {request.data.get('name')}")
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            logger.warning(f"Class creation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error creating fitness class: {str(e)}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request,pk):
        """Update an existing fitness class."""
        try:
            class_id = pk
            if not class_id:
                logger.warning("Class ID missing in update request")
                return Response(
                    {"error": "Class ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                fitness_class = FitnessClass.objects.get(id=class_id)
            except FitnessClass.DoesNotExist:
                logger.warning(f"Class not found: ID {class_id}")
                return Response(
                    {"error": "Class not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = FitnessClassSerializer(fitness_class, data=request.data, partial=True)
            if serializer.is_valid():
                with transaction.atomic():
                    if 'total_slots' in request.data:
                        current_bookings = fitness_class.bookings.count()
                        new_total_slots = int(request.data['total_slots'])
                        fitness_class.available_slots = max(0, new_total_slots - current_bookings)
                    serializer.save()
                    logger.info(f"Updated fitness class: {request.data.get('name', fitness_class.name)}")
                    return Response(serializer.data, status=status.HTTP_200_OK)

            logger.warning(f"Class update failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error updating fitness class: {str(e)}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class BookingView(APIView):
    """Handles CRUD operations for bookings."""

    def get(self, request):
        """Retrieve bookings for a specific email."""
        try:

            bookings = Booking.objects.filter(booked_by=request.user.username).select_related('fitness_class')
            serializer = BookingSerializer(bookings, many=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Error retrieving bookings: {str(e)}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """Create a new booking for a fitness class."""
        try:
            serializer = BookingSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                with transaction.atomic():
                    fitness_class = serializer.validated_data['fitness_class']
                    if fitness_class.available_slots <= 0:
                        raise serializers.ValidationError("No available slots for this class")
                    fitness_class.available_slots -= 1
                    fitness_class.save()
                    booking = serializer.save()
                    booking.booked_by = request.user.username if request.user.is_authenticated else None
                    booking.save()
                    logger.info(f"Booking created for {request.data.get('client_email')}")
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            logger.warning(f"Booking creation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error creating booking: {str(e)}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request):
        """Cancel a booking."""
        try:
            booking_id = request.data.get('id')
            if not booking_id:
                logger.warning("Booking ID missing in delete request")
                return Response(
                    {"error": "Booking ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                booking = Booking.objects.get(id=booking_id)
            except Booking.DoesNotExist:
                logger.warning(f"Booking not found: ID {booking_id}")
                return Response(
                    {"error": "Booking not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            with transaction.atomic():
                booking.fitness_class.available_slots += 1
                booking.fitness_class.save()
                booking.delete()
                logger.info(f"Cancelled booking {booking_id} for {booking.client_email}")
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            logger.error(f"Error cancelling booking: {str(e)}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )