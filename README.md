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

## Models diagram
<img width="2613" height="1518" alt="image" src="https://github.com/user-attachments/assets/f1bb739f-3fcf-4f5e-b7d2-f7ab5a9d1009" />


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


## Telegram Bot Setup

The project supports Telegram notifications via a bot.

### 1. Create a Telegram Bot
- Open Telegram and start a chat with **@BotFather**
- Create a new bot using `/newbot`
- Save the generated **BOT_TOKEN**

### 2. Get your Chat ID
- Start a chat with your bot or add the bot to group chat as admin
- Send any message to it
- Open in browser:
  `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates` (paste your BOT_TOKEN)
- Copy the `chat.id` value

### 3. Environment variables

Add the following variables to your `.env` file:

```env
TELEGRAM_BOT_TOKEN="your_bot_token"
TELEGRAM_CHAT_ID="your_chat_id"
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

* Custom `AUTH_USER_MODEL` (`users.User`)
* Database configuration via `settings.py`
* Celery & Redis configuration for background tasks
* Global pagination settings
* Shared base templates for API browsable interface
