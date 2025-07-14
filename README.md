# 🏋️‍♂️ Fitness Studio Booking System – Backend API

This is a Django REST Framework API for managing fitness classes and bookings. It enables users to create, view, update, and cancel bookings with validations such as timezones, slot availability, and duplicate detection.

---

## 📚 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [API Endpoints](#api-endpoints)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

---

## ✅ Features

- Create, update, and retrieve fitness classes (Yoga, Zumba, HIIT).
- Timezone-aware scheduling with `Asia/Kolkata` default.
- Book and cancel reservations with email-based validation.
- Duplicate booking and slot validation.
- Admin dashboard for class and booking management.
- Built-in unit tests for core functionality.
- Logging for improved debugging and tracking.

---

## 🧰 Tech Stack

- **Backend:** Django 4.x, Django REST Framework
- **Database:** SQLite (default) — easily extendable to PostgreSQL/MySQL
- **Language:** Python 3.8+
- **Timezone Handling:** `pytz`
- **Testing:** Django Test Framework
- **Environment Management:** `.env` file support

---

## 🛠️ Prerequisites

- Python 3.8+
- `pip` – Python package manager
- `virtualenv` – (Recommended) Virtual environment manager
- Git

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Nitesh6206/fitness-studio-booking.git
cd fitness-studio-booking
```

### 2. Create & Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> If `requirements.txt` is missing:
```bash
pip install django djangorestframework pytz
```

### 4. Configure Environment Variables

Create a `.env` file in the root with:

```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
TIME_ZONE=Asia/Kolkata
```

Generate `SECRET_KEY` via tools like [djecrety](https://djecrety.ir/).

### 5. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Access:
- API: [http://localhost:8000/](http://localhost:8000/)
- Admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## 🔗 API Endpoints

### Base URL: `http://localhost:8000/`

---

### 🔹 `/classes/`

- **GET** – Retrieve upcoming fitness classes  
  **Query:** `timezone` (optional)  
  **Example:**  
  ```bash
  curl http://localhost:8000/classes/?timezone=Asia/Kolkata
  ```

- **POST** – Create a new fitness class  
  **Body:**
  ```json
  {
    "name": "YOGA",
    "date_time": "2025-06-14T09:00:00+05:30",
    "instructor": "Raj",
    "total_slots": 10,
    "available_slots": 8
  }
  ```

- **PUT** – Update an existing fitness class  
  **Body:**
  ```json
  {
    "id": 1,
    "instructor": "Jane",
    "total_slots": 15
  }
  ```

---

### 🔹 `/bookings/`

- **GET** – Get bookings for an email  
  **Auth Required**  
  **Query:** `email=test@example.com`  
  **Example:**  
  ```bash
  curl -H "Authorization: Bearer your-token" http://localhost:8000/bookings/?email=test@example.com
  ```

- **POST** – Book a fitness class  
  **Body:**
  ```json
  {
    "class_id": 1,
    "client_name": "Test User",
    "client_email": "test@example.com",
    "booking_time": "2025-06-13T10:00:00+05:30"
  }
  ```

- **DELETE** – Cancel a booking  
  **Body:**
  ```json
  {
    "id": 1
  }
  ```

---

## 💻 Usage Examples

### ✅ Create a Fitness Class

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "name": "ZUMBA",
  "date_time": "2025-06-15T10:00:00+05:30",
  "instructor": "Priya",
  "total_slots": 12
}' http://localhost:8000/classes/
```

### 📅 Book a Class (Authenticated)

```bash
curl -X POST -H "Authorization: Bearer <your-token>" -H "Content-Type: application/json" -d '{
  "class_id": 1,
  "client_name": "Test User",
  "client_email": "test@example.com"
}' http://localhost:8000/bookings/
```

---

## 🧪 Testing

```bash
python manage.py test
```

> ✅ 14 test cases included:
- Class creation & validation
- Booking logic & duplication check
- Authorization and error handling

---

## 🙋‍♂️ Contributing

1. Fork the repo
2. Create your branch:
   ```bash
   git checkout -b feature/awesome-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add: New Feature"
   ```
4. Push:
   ```bash
   git push origin feature/awesome-feature
   ```
5. Submit a pull request!

---

## 👨‍💻 Author

**Nitesh Kumar**  
📧 [niteshsingh6206@gmail.com](mailto:niteshsingh6206@gmail.com)  
🌐 [GitHub](https://github.com/Nitesh6206)

---

## 📜 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.
