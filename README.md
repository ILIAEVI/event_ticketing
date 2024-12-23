# Django API with Authentication, Event Management, and Contact Features

This project is a Django-based web application providing various features, including user authentication, event
management with booking and queue, and contact management with email answering functionalities for admins.

- **Authentication**: User sign-up, login, email verification, password reset, and JWT-based authentication.
- **Event Management**: Event creation, categorization, ticket batching, booking with QR code generation and queue
  system.
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
- **Category**: Events can be categorized for better organization. Categories can be created by staff.
- **Ticket Batch**: Tickets are grouped in batches, and each batch can have its own category(vip, standard) and ticket
  quantity.
- **Booking**: Users can book tickets for events. The ticket booking process is wrapped in an atomic transaction. A
  locking mechanism is implemented to prevent multiple processes from modifying the same resource simultaneously.

## Redis Queue and Celery Task

The project utilizes Redis as a queue system to handle ticket booking requests. The task is processed using Celery,
which runs every 10 minutes to process the queue.

### How it Works:

1. **Queue System**: When Event queue is active and user attempts to book a ticket, the user is placed in the Redis
   queue.
2. **Celery Task**: A Celery task is scheduled to run every 10 minutes. This task processes the users in the queue.
3. **Booking Limit**: The task processes a maximum of 100 user per cycle. It generates unique booking tokens for each
   user. With this booking tokens, user can access booking endpoint and finish booking.
4. **Booking Token** The booking token has expiration time, 10 minutes.
5. **Queue Management**: If the number of requests exceeds 100 users, those users remain in the queue until the next
   processing cycle.

This system ensures that only a limited number of users can book tickets at a time, avoiding overload and providing fair
access to the booking system.

### Contact Management

- **Contact Us**: Allows users to submit contact form and send email to administration.
- **Contact List** There is implemented received contact forms list. where staff can send back email. there is
  implemented custom ordering for phone_numbers.
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
- **POST** `/api/auth/logout/` - Log out and black list token
- **GET** `/api/auth/verify_email/<token>/` - Verify user email address.
- **POST** `/api/auth/password_reset_request/` - Request a password reset email.
- **POST** `/api/auth/password_reset_confirm/<token>/` - Confirm password reset.

### Event Management

- **GET** `/api/event/` - List all events or retrieve.
- **POST** `/api/event/` - Create a new event.
- **GET** `/api/category/` - List all event categories.
- **GET** `/api/ticket_batch/` - List all ticket batches or retrieve.
- **POST** `/api/ticket_batch/` - Create a new ticket batch.
- **GET** `/api/booking/` - List user's bookings.
- **GET** `/api/booking/<id>/get-qr-code/` - return string for qr code
- **GET** `/api/event/<id>/start_booking/` - Custom action to start booking/
- **GET** `/api/event/<id>/queue/` - Waiting room imitation
- **POST** `/api/event/<id>/booking` - Custom action to complete booking of specific event

### Contact Management

- **GET** `/api/contacts/` - List all contact information.
- **POST** `/api/contact_us/` - Contact Us endpoint.
- **POST** `/api/contacts/send_email/` - send_email endpoints for staff, to answer received emails.
- **GET** `/api/social_media/` - List all social media links.
- **POST** `/api/social_media/` - Add new social media link.
