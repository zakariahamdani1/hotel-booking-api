# Hotel Booking API

A RESTful Hotel Booking API built with Django and Django REST Framework.

## Overview

This project provides a backend API for managing hotel rooms, customers, and bookings.

It includes authentication, role-based permissions, room availability checking, booking validation, automatic price calculation, cancellation, and booking completion.

## Features

* Customer registration and login
* Token-based authentication
* Customer profile access
* Room listing and management
* Manager-only room creation, update, and deletion
* Room availability checking by date
* Create and manage bookings
* Automatic booking price calculation
* Prevention of overlapping bookings
* Booking cancellation
* Manager-only booking completion
* Automated API tests

## Technologies

* Python
* Django
* Django REST Framework
* SQLite
* Token Authentication
* Django Test Framework

## Authentication

The API uses token-based authentication.

After logging in, the client receives an authentication token.

Include the token in subsequent authenticated requests:

```text
Authorization: Token <your-token>
```

## API Endpoints

### Authentication

| Method | Endpoint     | Description                              |
| ------ | ------------ | ---------------------------------------- |
| POST   | `/register/` | Register a new customer                  |
| POST   | `/login/`    | Login and obtain an authentication token |

### Customers

| Method    | Endpoint           | Description                                  |
| --------- | ------------------ | -------------------------------------------- |
| GET       | `/customers/`      | List customers available to the current user |
| GET       | `/customers/<id>/` | Retrieve a customer                          |
| PUT/PATCH | `/customers/<id>/` | Update a customer                            |
| DELETE    | `/customers/<id>/` | Delete a customer                            |

### Rooms

| Method    | Endpoint            | Description                             |
| --------- | ------------------- | --------------------------------------- |
| GET       | `/rooms/`           | List rooms                              |
| POST      | `/rooms/`           | Create a room (manager only)            |
| GET       | `/rooms/<id>/`      | Retrieve a room                         |
| PUT/PATCH | `/rooms/<id>/`      | Update a room (manager only)            |
| DELETE    | `/rooms/<id>/`      | Delete a room (manager only)            |
| GET       | `/rooms/available/` | Find available rooms for selected dates |

### Bookings

| Method    | Endpoint                   | Description                       |
| --------- | -------------------------- | --------------------------------- |
| GET       | `/bookings/`               | List the current user's bookings  |
| POST      | `/bookings/`               | Create a booking                  |
| GET       | `/bookings/<id>/`          | Retrieve a booking                |
| PUT/PATCH | `/bookings/<id>/`          | Update a booking                  |
| DELETE    | `/bookings/<id>/`          | Delete a booking                  |
| POST      | `/bookings/<id>/cancel/`   | Cancel a booking                  |
| POST      | `/bookings/<id>/complete/` | Complete a booking (manager only) |

## Booking Logic

The API prevents two confirmed bookings from occupying the same room during overlapping dates.

For example:

```text
Booking A
01 Sep → 06 Sep

Booking B
03 Sep → 05 Sep

❌ Overlap
```

But:

```text
Booking A
01 Sep → 06 Sep

Booking B
06 Sep → 10 Sep

✅ No overlap
```

The total booking price is calculated automatically from the room price and the number of nights.

## Permissions

The project distinguishes between regular customers and managers.

### Customers

Customers can:

* View their own customer information
* View their own bookings
* Create bookings
* Cancel their bookings
* Access publicly available room information

### Managers

Managers can additionally:

* Create rooms
* Update rooms
* Delete rooms
* View all customers
* View all bookings
* Complete bookings

## Testing

The project includes automated API tests covering authentication, permissions, room management, booking creation, booking conflicts, cancellation, booking isolation, and booking completion.

Current test result:

```text
Found 16 test(s).
................
Ran 16 tests
OK
```

Run the test suite with:

```bash
python manage.py test
```

## Installation

Clone the repository:

```bash
git clone https://github.com/zakariahamdani1/hotel-booking-api.git
cd hotel-booking-api
```

Create and activate a virtual environment:

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key
```

Apply migrations:

```bash
python manage.py migrate
```

Run the development server:

```bash
python manage.py runserver
```

The API will then be available at:

```text
http://127.0.0.1:8000/
```

## Project Structure

```text
hotel-booking-api/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── hotel/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── permissions.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

## Author

Zakaria Hamdani

This project was built as a practical Django REST Framework project to develop backend development and API design skills.
