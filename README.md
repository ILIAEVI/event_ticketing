# Django API with Authentication, Event Management, and Contact Features

This project is a Django-based web application providing various features, including user authentication, event
management with booking and queue, and contact management. The project leverages Django REST Framework for building APIs
and includes the use of JWT for authentication. The following modules are included in this project:

- **Authentication**: User sign-up, login, email verification, password reset, and JWT-based authentication.
- **Event Management**: Event creation, categorization, ticket batching, booking and queue system.
- **Contact Management**: Contact information handling with email answering functionalities for admins and social media
  links.

## Features

### Authentication

- **Signup**: Allows users to sign up by providing their email and password.
- **Login**: Users can log in with their credentials to receive a JWT token for authentication.
- **Verify Email**: Users can verify their email to activate their account.
- **Logout**: Users can log out and blacklist their refresh token.
- **Password Reset**: Allows users to reset their password via email.

### Event Management

- **Event**: Allows creation, categorization, and management of events.
- **Category**: Events can be categorized for better organization.
- **Ticket Batch**: Tickets are grouped in batches, and each batch can have its own details.
- **Booking**: Users can book tickets for events. The ticket booking process is wrapped in an atomic transaction. A
  locking mechanism is implemented to prevent multiple processes from modifying the same resource simultaneously.

## Redis Queue and Celery Task

The project utilizes **Redis** as a queue system to handle ticket booking requests. The task is processed using Celery,
which runs every 10 minutes to process the queue.

### How it Works:

1. **Queue System**: When a user attempts to book a ticket, the request is placed in the Redis queue.
2. **Celery Task**: A Celery task is scheduled to run every 10 minutes. This task processes the requests in the queue.
3. **Booking Limit**: The task processes a maximum of 10 user requests per cycle. It allows up to 10 users to book a
   ticket and generates a unique booking token for each successful booking.
4. **Response**: Once the users have been processed, they receive a booking token and other relevant details about the
   booking (e.g., event details, ticket validity, etc.).
5. **Queue Management**: If the number of requests exceeds 10 users, those users remain in the queue until the next
   processing cycle.

This system ensures that only a limited number of users can book tickets at a time, avoiding overload and providing fair
access to the booking system.

### Contact Management

- **Contact Us**: Allows users to submit inquiries or messages.
- **Social Links**: Provides links to the organization's social media profiles.

## Installation

### Setup

2. Create and activate virtual environment and then install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Before running migrations ensure that docker is running. open docker-desktop, and run:
    ```bash
    docker-compose build
    docker-compose up -d
    ```

3. Apply migrations:
    ```bash
    python manage.py migrate
    ```

4. Create a superuser (optional):
    ```bash
    python manage.py createsuperuser
    ```

5. Run the server:
    ```bash
    python manage.py runserver
    ```

## API Endpoints

### Authentication

- **POST** `/api/auth/signup/` - Register a new user.
- **POST** `/api/auth/login/` - Log in and get a JWT token.
- **GET** `/api/auth/verify_email/<token>/` - Verify user email address.
- **POST** `/api/auth/password_reset_request/` - Request a password reset email.
- **POST** `/api/auth/password_reset_confirm/<token>/` - Confirm password reset.

### Event Management

- **GET** `/api/event/` - List all events.
- **POST** `/api/event/` - Create a new event.
- **GET** `/api/category/` - List all event categories.
- **POST** `/api/category/` - Create a new category.
- **GET** `/api/ticket_batch/` - List all ticket batches.
- **POST** `/api/ticket_batch/` - Create a new ticket batch.
- **GET** `/api/booking/` - List all bookings.
- **POST** `/api/booking/` - Create a new booking.

### Contact Management

- **GET** `/api/contact/` - List all contact information.
- **POST** `/api/contact/` - Add new contact information.
- **GET** `/api/social_links/` - List all social media links.
- **POST** `/api/social_links/` - Add new social media link.

## URL Configuration

The URLs are organized into several namespaces:

- `/api/` - Event-related URLs (`event`, `category`, `ticket_batch`, `booking`).
- `/api/contact/` - Contact-related URLs (`contact_us`, `contacts`, `social_links`).
- `/api/auth/` - Authentication-related URLs (`signup`, `login`, `logout`, `password_reset_request`,
  `password_reset_confirm`).
- `/admin/` - Django admin interface.

