"""
Models for fitness classes and bookings.
"""
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator

class FitnessClass(models.Model):
    """Model representing a fitness class."""
    
    CLASS_TYPES = [
        ('YOGA', 'Yoga'),
        ('ZUMBA', 'Zumba'),
        ('HIIT', 'HIIT'),
    ]

    name = models.CharField(max_length=100, choices=CLASS_TYPES)
    date_time = models.DateTimeField()
    instructor = models.CharField(max_length=100)
    total_slots = models.PositiveIntegerField(default=10)
    available_slots = models.PositiveIntegerField()
    duration=models.CharField(max_length=50, null=True)
    Location=models.CharField(max_length=200,null=True)

    class Meta:
        ordering = ['date_time']
        verbose_name = 'Fitness Class'
        verbose_name_plural = 'Fitness Classes'

    def clean(self):
        """Validate model fields."""
        if self.available_slots > self.total_slots:
            raise ValidationError("Available slots cannot exceed total slots")
        if self.date_time < timezone.now():
            raise ValidationError("Cannot schedule class in the past")

    def save(self, *args, **kwargs):
        """Save model with validation and set available_slots on creation."""
        if not self.pk:  # On creation
            self.available_slots = self.total_slots
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_name_display()} with {self.instructor} at {self.date_time}"

class Booking(models.Model):
    """Model representing a booking for a fitness class."""
    
    fitness_class = models.ForeignKey(
        FitnessClass, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField(validators=[EmailValidator()])
    booking_time = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['fitness_class', 'client_email']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'

    def clean(self):
        """Validate booking constraints."""
        if self.fitness_class.date_time < timezone.now():
            raise ValidationError("Cannot book a class that has already occurred")
        if self.fitness_class.available_slots <= 0:
            raise ValidationError("No slots available for this class")
        if self.booking_time > self.fitness_class.date_time:
            raise ValidationError("Cannot book after class start time")
        if Booking.objects.filter(
            fitness_class=self.fitness_class,
            client_email=self.client_email
        ).exclude(id=self.id).exists():
            raise ValidationError("This email has already booked this class")

    def save(self, *args, **kwargs):
        """Save booking with validation and update available slots."""
        self.full_clean()
        if not self.pk:  # New booking
            if self.fitness_class.available_slots <= 0:
                raise ValidationError("No slots available for this class")
            self.fitness_class.available_slots -= 1
            self.fitness_class.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client_name} booked {self.fitness_class}"