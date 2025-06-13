# Fitness Studio Booking System

A Django REST Framework API for managing fitness classes and bookings. Users can create, view, and update fitness classes (e.g., Yoga, Zumba, HIIT) and book or cancel reservations with validation for availability, timezones, and duplicates.

## Table of Contents
- [Features](#features)
- [Technologies](#technologies)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [API Endpoints](#api-endpoints)
- [Usage](#usage)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Features
- Create, retrieve, and update fitness classes with timezone-aware scheduling.
- Book and cancel class reservations with email-based authorization.
- Validate class slots, future dates, and duplicate bookings.
- Comprehensive logging for debugging.
- Unit tests for API functionality.
- Admin panel for managing classes and bookings.

## Technologies
- **Backend**: Django 4.x, Django REST Framework
- **Database**: SQLite (default, supports PostgreSQL/MySQL)
- **Python**: 3.8+
- **Dependencies**: Managed via `requirements.txt`
- **Timezone Handling**: `pytz`
- **Testing**: Django test framework

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtualenv (recommended)
- Git
- Terminal or command prompt

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/fitness-studio-booking.git
   cd fitness-studio-booking


2. **Create and Activate a Virtual Environment**
- python -m venv venv
- source venv/bin/activate  # On Windows: venv\Scripts\activate


3. **Install Dependencies**
- pip install -r requirements.txt

Note: If requirements.txt is not provided, install core dependencies:
pip install django djangorestframework pytz


**Configure Environment VariablesCreate a .env file in the project root and add the following:**
- SECRET_KEY=your-django-secret-key right now not using but use may be in future
- DEBUG=True
- ALLOWED_HOSTS=localhost,127.0.0.1
- TIME_ZONE=Asia/Kolkata

Generate a secure SECRET_KEY using a tool like Djecrety.

**Apply Migrations**
- python manage.py makemigrations
- python manage.py migrate


**Create a Superuser (Optional)For admin access:**
- python manage.py createsuperuser


**Run the Development Server**
_python manage.py runserver

Access the API at http://localhost:8000/ and the admin panel at http://localhost:8000/admin/.


## API Endpoints
Base URL
 http://localhost:8000/ 
1. Fitness Classes (/classes/)
Handles CRUD operations for fitness classes.

GET /classes/

Description: Retrieve upcoming fitness classes with optional timezone filtering.
Query Parameters:
timezone (optional): Timezone name (e.g., Asia/Kolkata). Default: Asia/Kolkata.


Response:
200 OK: List of classes with details (id, name, class_type, date_time, instructor, total_slots, available_slots).
400 Bad Request: Invalid timezone.
500 Internal Server Error: Server error.


Example:curl http://localhost:8000/classes/?timezone=Asia/Kolkata




POST /classes/

Description: Create a new fitness class.
Request Body (JSON):{
  "name": "YOGA",
  "date_time": "2025-06-14T09:00:00+05:30",
  "instructor": "Raj",
  "total_slots": 10,
  "available_slots": 8
}


name: Must be YOGA, ZUMBA, or HIIT.
date_time: ISO 8601 format, future date/time.
total_slots: Positive integer.
available_slots: Optional, defaults to total_slots.


Response:
201 Created: Class created with details.
400 Bad Request: Invalid data (e.g., past date, invalid class type).
500 Internal Server Error: Server error.


Example:curl -X POST -H "Content-Type: application/json" -d '{"name":"YOGA","date_time":"2025-06-14T09:00:00+05:30","instructor":"Raj","total_slots":10,"available_slots":8}' http://localhost:8000/classes/




PUT /classes/

Description: Update an existing fitness class.
Request Body (JSON):{
  "id": 1,
  "instructor": "Jane",
  "total_slots": 15
}


id: Required, class ID.
Other fields are optional (partial update).


Response:
200 OK: Updated class details.
400 Bad Request: Invalid data or missing ID.
404 Not Found: Class not found.
500 Internal Server Error: Server error.


Example:curl -X PUT -H "Content-Type: application/json" -d '{"id":1,"instructor":"Jane","total_slots":15}' http://localhost:8000/classes/





2. Bookings (/bookings/)
Handles CRUD operations for bookings.

GET /bookings/

Description: Retrieve bookings for a specific email.
Query Parameters:
email: Required, client email address.


Authentication: Required (user must be authenticated and match the email or be a superuser).
Response:
200 OK: List of bookings with details (id, class_id, client_name, client_email, booking_time).
400 Bad Request: Missing email parameter.
401 Unauthorized: Not authenticated.
403 Forbidden: Unauthorized to view bookings for the email.
500 Internal Server Error: Server error.


Example:curl -H "Authorization: Bearer your-token" http://localhost:8000/bookings/?email=test@example.com




POST /bookings/

Description: Create a new booking for a fitness class.
Request Body (JSON):{
  "class_id": 1,
  "client_name": "Test User",
  "client_email": "test@example.com",
  "booking_time": "2025-06-13T10:00:00+05:30"
}


class_id: Required, ID of an upcoming class.
client_email: Valid email address.
booking_time: Optional, defaults to current time (must be before class start).


Authentication: Required.
Response:
201 Created: Booking created with details.
400 Bad Request: Invalid data (e.g., invalid email, duplicate booking, booking after class start).
401 Unauthorized: Not authenticated.
500 Internal Server Error: Server error.


Example:curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer your-token" -d '{"class_id":1,"client_name":"Test User","client_email":"test@example.com","booking_time":"2025-06-13T10:00:00+05:30"}' http://localhost:8000/bookings/




DELETE /bookings/

Description: Cancel a booking.
Request Body (JSON):{
  "id": 1
}


id: Required, booking ID.


Authentication: Required (user must match booking email or be a superuser).
Response:
204 No Content: Booking cancelled.
400 Bad Request: Missing ID.
401 Unauthorized: Not authenticated.
403 Forbidden: Unauthorized to cancel the booking.
404 Not Found: Booking not found.
500 Internal Server Error: Server error.


Example:curl -X DELETE -H "Content-Type: application/json" -H "Authorization: Bearer your-token" -d '{"id":1}' http://localhost:8000/bookings/





Usage

Create a Fitness ClassUse the POST /classes/ endpoint to schedule a new class. Example:
{
  "name": "ZUMBA",
  "date_time": "2025-06-15T10:00:00+05:30",
  "instructor": "Priya",
  "total_slots": 12
}


Book a ClassAuthenticate a user and use the POST /bookings/ endpoint to reserve a slot. Ensure the class has available slots and the booking time is valid.

View BookingsUse the GET /bookings/ endpoint with an email parameter to list all bookings for a user. Requires authentication.

Cancel a BookingUse the DELETE /bookings/ endpoint with the booking ID to cancel a reservation. Only the booking owner or a superuser can cancel.




**Admin PanelAccess the Django admin at http://localhost:8000/admin/ to manage classes and bookings manually.**


Testing
- Run the test suite to verify API functionality:
- python manage.py test

**The project includes 14 tests covering:**

_ Fitness class creation, retrieval, and validation.
- Booking creation, cancellation, and duplicate checks.
- Authentication and authorization checks.
- Error handling for invalid inputs (e.g., email, timezone).

To add tests, modify booking/tests.py or create new test cases.
Contributing

**Fork the repository.**
- Create a feature branch (git checkout -b feature/your-feature).
- Commit changes (git commit -m "Add your feature").
- Push to the branch (git push origin feature/your-feature).
- Open a pull request.

**License**
MIT License. See LICENSE for details.

Project developed by Nitesh Kumar.For support, contact: niteshsingh6206@gmail.com or GitHub Issues.
