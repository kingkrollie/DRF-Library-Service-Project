# Library Service

Library management system
Built with Django REST Framework

## Description

**Library Service** is a web-based application designed to manage books, borrowings, and users in a library.
The system allows librarians to track books, monitor borrowings, handle overdue notifications, and manage user accounts
efficiently.

The project improves workflow by providing structured API endpoints, automated daily notifications for overdue
borrowings, and comprehensive test coverage to ensure reliability.
It follows Django and DRF best practices, including viewsets, serializers, permissions, and Celery for background tasks.

## Installing / Getting Started

### Prerequisites

* Docker
* Docker Compose
* Python 3.10+ (for local testing, optional)
* PostgreSQL (if not using Docker defaults)
* Redis (for Celery tasks, if not using Docker defaults)

### Setup with Docker

```bash
git clone https://github.com/yourusername/library-service.git
cd library-service
docker-compose up --build
```

If you run app for the first time, there will be a notification from Stripe in the console with a 
link to authentication. By clicking on the link you need to authenticate, log in to your 
account, copy and add **STRIPE_PUBLIC_KEY** and **STRIPE_SECRET_KEY** to the **.env** file.  
***(you will probably have to restart the docker with command  <ins>docker-compose up</ins>)***  
After that, there will be a message like this:  

```
 Ready! You are using Stripe API Version ... 
 Your webhook signing secret is .....
```
this password must be inserted into the **.env** file to **STRIPE_WEBHOOK_SECRET**.  
After that, you don't need to do anything on subsequent launches.

The application will be available at:


http://127.0.0.1:8000/
```

### Creating Superuser and Loading Fixtures

Create a superuser inside the Docker container:

```bash
docker-compose exec library python manage.py createsuperuser
```

Load initial demo data fixture:

```bash
docker-compose exec library python manage.py loaddata fixtures/initial_data.json
```

## Running Tests

```bash
docker-compose exec library python manage.py test
```

## Features

* JWT Authentication system for users
* CRUD for Books and Borrowings
* View and manage overdue borrowings
* Daily notifications for overdue borrowings (via Celery + Redis)
* Swagger documentation for API endpoints
* Search, filtering, and pagination for list views
* Permissions: admin-only modifications, read-only for other users
* Optimized database queries with `select_related` and `prefetch_related`
* Unit tests for core functionality

## Configuration

* Custom `AUTH_USER_MODEL` (`accounts.Veterinarian` in example; replace as needed)
* Database configuration via `settings.py`
* Celery & Redis configuration for background tasks
* Global pagination settings
* Shared base templates for API browsable interface
