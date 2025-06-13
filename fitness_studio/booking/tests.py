"""
Tests for fitness class and booking APIs.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from django.urls import reverse
from .models import FitnessClass, Booking
import pytz
from datetime import timedelta
import json

class FitnessClassViewTests(TestCase):
    """Tests for FitnessClassView."""

    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()
        self.valid_class_data = {
            "name": "YOGA",
            "date_time": (timezone.now() + timedelta(days=1)).isoformat(),
            "instructor": "John Doe",
            "total_slots": 10
        }
        self.invalid_class_data = {
            "name": "INVALID",
            "date_time": (timezone.now() - timedelta(days=1)).isoformat(),
            "instructor": "John Doe",
            "total_slots": 0
        }

    def test_get_classes(self):
        """Test retrieving upcoming classes."""
        FitnessClass.objects.create(
            name="YOGA",
            date_time=timezone.now() + timedelta(days=1),
            instructor="John Doe",
            total_slots=10,
            available_slots=10
        )
        response = self.client.get(reverse('class-list'), {'timezone': 'Asia/Kolkata'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'YOGA')
        self.assertEqual(response.data[0]['instructor'], 'John Doe')

    def test_get_classes_invalid_timezone(self):
        """Test retrieving classes with invalid timezone."""
        response = self.client.get(reverse('class-list'), {'timezone': 'Invalid/Timezone'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid timezone')

    def test_create_class_success(self):
        """Test creating a new class with valid data."""
        response = self.client.post(
            reverse('class-list'),
            data=json.dumps(self.valid_class_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FitnessClass.objects.count(), 1)
        self.assertEqual(response.data['name'], 'YOGA')
        self.assertEqual(response.data['available_slots'], 10)

    def test_create_class_invalid_data(self):
        """Test creating a class with invalid data."""
        response = self.client.post(
            reverse('class-list'),
            data=json.dumps(self.invalid_class_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('date_time', response.data)
        self.assertIn('total_slots', response.data)

    def test_update_class_success(self):
        """Test updating an existing class."""
        fitness_class = FitnessClass.objects.create(
            name="YOGA",
            date_time=timezone.now() + timedelta(days=1),
            instructor="John Doe",
            total_slots=10,
            available_slots=10
        )
        update_data = {
            "id": fitness_class.id,
            "instructor": "Jane Smith",
            "total_slots": 15
        }
        response = self.client.put(
            reverse('class-list'),
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        fitness_class.refresh_from_db()
        self.assertEqual(fitness_class.instructor, 'Jane Smith')
        self.assertEqual(fitness_class.total_slots, 15)
        self.assertEqual(fitness_class.available_slots, 15)

    def test_update_class_not_found(self):
        """Test updating a non-existent class."""
        update_data = {
            "id": 999,
            "instructor": "Jane Smith"
        }
        response = self.client.put(
            reverse('class-list'),
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Class not found')

class BookingViewTests(TestCase):
    """Tests for BookingView."""

    def setUp(self):
        """Set up test data, client, and user."""
        self.client = APIClient()
        self.user = type('User', (), {
            'email': 'test@example.com',
            'is_superuser': False,
            'is_authenticated': True
        })()
        self.fitness_class = FitnessClass.objects.create(
            name="ZUMBA",
            date_time=timezone.now() + timedelta(days=1),
            instructor="John Doe",
            total_slots=10,
            available_slots=10
        )
        self.valid_booking_data = {
            "class_id": self.fitness_class.id,
            "client_name": "Test User",
            "client_email": "test@example.com",
            "booking_time": timezone.now().isoformat()
        }
        self.invalid_booking_data = {
            "class_id": self.fitness_class.id,
            "client_name": "Test User",
            "client_email": "invalid-email",
            "booking_time": (self.fitness_class.date_time + timedelta(hours=1)).isoformat()
        }

    def test_create_booking_success(self):
        """Test creating a booking with valid data."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('booking-list'),
            data=json.dumps(self.valid_booking_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)
        self.fitness_class.refresh_from_db()
        self.assertEqual(self.fitness_class.available_slots, 9)

    def test_create_booking_invalid_data(self):
        """Test creating a booking with invalid data."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('booking-list'),
            data=json.dumps(self.invalid_booking_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('client_email', response.data)
        self.assertIn('booking_time', response.data)
        self.assertEqual(response.data['client_email'], ['Enter a valid email address.'])
        self.assertEqual(response.data['booking_time'], ['Cannot book after class start time'])

    def test_create_duplicate_booking(self):
        """Test creating a duplicate booking."""
        self.client.force_authenticate(user=self.user)
        self.client.post(
            reverse('booking-list'),
            data=json.dumps(self.valid_booking_data),
            content_type='application/json'
        )
        response = self.client.post(
            reverse('booking-list'),
            data=json.dumps(self.valid_booking_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This email has already booked this class', str(response.data))

    def test_get_bookings(self):
        """Test retrieving bookings for an authorized user."""
        Booking.objects.create(
            fitness_class=self.fitness_class,
            client_name="Test User",
            client_email="test@example.com",
            booking_time=timezone.now()
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('booking-list'), {'email': 'test@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['client_email'], 'test@example.com')

    def test_get_bookings_unauthorized(self):
        """Test retrieving bookings for an unauthorized user."""
        Booking.objects.create(
            fitness_class=self.fitness_class,
            client_name="Test User",
            client_email="test@example.com",
            booking_time=timezone.now()
        )
        other_user = type('User', (), {
            'email': 'other@example.com',
            'is_superuser': False,
            'is_authenticated': True
        })()
        self.client.force_authenticate(user=other_user)
        response = self.client.get(reverse('booking-list'), {'email': 'test@example.com'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Unauthorized to view bookings for this email')

    def test_get_bookings_no_email(self):
        """Test retrieving bookings without providing an email."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('booking-list'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Email parameter is required')

    def test_delete_booking_success(self):
        """Test deleting a booking as an authorized user."""
        self.client.force_authenticate(user=self.user)
        booking = Booking.objects.create(
            fitness_class=self.fitness_class,
            client_name="Test User",
            client_email="test@example.com",
            booking_time=timezone.now()
        )
        response = self.client.delete(
            reverse('booking-list'),
            data=json.dumps({'id': booking.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Booking.objects.count(), 0)
        self.fitness_class.refresh_from_db()
        self.assertEqual(self.fitness_class.available_slots, 10)

    def test_delete_booking_unauthorized(self):
        """Test deleting a booking as an unauthorized user."""
        other_user = type('User', (), {
            'email': 'other@example.com',
            'is_superuser': False,
            'is_authenticated': True
        })()
        self.client.force_authenticate(user=other_user)
        booking = Booking.objects.create(
            fitness_class=self.fitness_class,
            client_name="Test User",
            client_email="test@example.com",
            booking_time=timezone.now()
        )
        response = self.client.delete(
            reverse('booking-list'),
            data=json.dumps({'id': booking.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Unauthorized to cancel this booking')