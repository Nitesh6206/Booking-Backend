"""
URL configuration for booking app.
"""
from django.urls import path
from .views import FitnessClassView, BookingView

urlpatterns = [
    path('classes/', FitnessClassView.as_view(), name='class-list'),
    path('classes/<int:pk>/', FitnessClassView.as_view(), name='class-list'),
    path('bookings/', BookingView.as_view(), name='booking-list'),
]