"""
Serializers for fitness classes and bookings.
"""
from rest_framework import serializers
from django.utils import timezone
from .models import FitnessClass, Booking
import pytz

class FitnessClassSerializer(serializers.ModelSerializer):
    """Serializer for FitnessClass model."""
    
    class_type = serializers.CharField(source='get_name_display', read_only=True)

    class Meta:
        model = FitnessClass
        fields = ['id', 'name', 'class_type', 'date_time', 'instructor', 'total_slots', 'available_slots']
        extra_kwargs = {
            'available_slots': {'required': False}
        }

    def validate_name(self, value):
        """Validate class type is one of the allowed choices."""
        if value not in dict(FitnessClass.CLASS_TYPES).keys():
            raise serializers.ValidationError("Invalid class type. Choose from: YOGA, ZUMBA, HIIT")
        return value

    def validate_date_time(self, value):
        """Validate date_time is in the future and in correct format."""
        try:
            if isinstance(value, str):
                value = pytz.timezone('Asia/Kolkata').localize(
                    timezone.datetime.fromisoformat(value.replace('Z', '+00:00'))
                )
            if value < timezone.now():
                raise serializers.ValidationError("Class date/time cannot be in the past")
        except ValueError:
            raise serializers.ValidationError(
                "Invalid date_time format. Use ISO 8601 (e.g., '2025-06-14T09:00:00+05:30')"
            )
        return value

    def validate_total_slots(self, value):
        """Validate total_slots is positive."""
        if value <= 0:
            raise serializers.ValidationError("Total slots must be greater than 0")
        return value

    def validate(self, data):
        """Validate available_slots does not exceed total_slots."""
        if 'available_slots' in data and data['available_slots'] > data.get(
            'total_slots', self.instance.total_slots if self.instance else 0
        ):
            raise serializers.ValidationError("Available slots cannot exceed total slots")
        return data

    def create(self, validated_data):
        """Set available_slots to total_slots if not provided."""
        if 'available_slots' not in validated_data:
            validated_data['available_slots'] = validated_data['total_slots']
        return super().create(validated_data)

class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model."""
    
    class_id = serializers.PrimaryKeyRelatedField(
        queryset=FitnessClass.objects.filter(date_time__gt=timezone.now()),
        source='fitness_class'
    )

    class Meta:
        model = Booking
        fields = ['id', 'class_id', 'client_name', 'client_email', 'booking_time']
        extra_kwargs = {
            'booking_time': {'required': False}
        }

    def validate(self, data):
        """Validate booking data."""
        errors = {}

        # Set default booking_time if not provided
        if 'booking_time' not in data:
            data['booking_time'] = timezone.now()

        # Validate booking_time
        if data['booking_time'] > data['fitness_class'].date_time:
            errors.setdefault('booking_time', []).append("Cannot book after class start time")

        # Check for duplicate booking
        if Booking.objects.filter(
            fitness_class=data['fitness_class'],
            client_email=data['client_email']
        ).exists():
            errors.setdefault('non_field_errors', []).append("This email has already booked this class")

        # Perform model-level validation
        try:
            instance = Booking(**data)
            instance.clean()
        except ValidationError as e:
            if hasattr(e, 'message_dict'):
                for field, messages in e.message_dict.items():
                    errors.setdefault(field, []).extend(messages)
            else:
                errors.setdefault('non_field_errors', []).extend(e.messages)
        except IntegrityError as e:
            # Handle unique constraint violation
            if 'unique constraint' in str(e).lower():
                errors.setdefault('non_field_errors', []).append("This email has already booked this class")

        if errors:
            raise serializers.ValidationError(errors)

        return data