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
        fields = ['id', 'name', 'class_type', 'date_time', 'instructor','duration','Location', 'total_slots', 'available_slots']
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
    fitness_class_details = FitnessClassSerializer(source='fitness_class', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'class_id', 'fitness_class_details', 'booking_time']
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
            print(data,"data................."),
        if Booking.objects.filter(
            fitness_class=data['fitness_class'],
            user_details=data.get('userprofile', None)
        ).exists():
            errors.setdefault('non_field_errors', []).append("This user has already booked this class")

        # Check available slots
        if data['fitness_class'].available_slots <= 0:
            errors.setdefault('class_id', []).append("No available slots for this class")

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

        if errors:
            raise serializers.ValidationError(errors)

        return data