# 🍔 Food Delivery System

A production-ready backend API for a comprehensive food delivery platform built with Django and modern technologies. This system handles user management, restaurant operations, menu management, shopping cart functionality, and real-time order tracking with WebSocket support.

## ✨ Features

### 🔐 Authentication & User Management
- **User Registration & Login** - Secure user account creation with email validation
- **Email OTP Verification** - Two-factor authentication with time-limited OTP codes
- **Password Reset Flow** - Secure password recovery via email OTP verification
- **Role-Based Access Control** - Four user roles: Admin, Restaurant, Customer, and Delivery personnel
- **User Profile Management** - Avatar uploads, theme preferences, contact information, and address management
- **Session Management** - Secure HTTP-only cookies with 14-day expiration

### 🏪 Restaurant & Menu Management
- **Restaurant Profiles** - Centralized restaurant management with logos, addresses, and contact details
- **Menu Categories** - Organized food categories (Drinks, Main Meals, Desserts, Snacks, Salads)
- **Menu Items** - Comprehensive menu with pricing, descriptions, and image uploads
- **Dynamic Menu API** - RESTful endpoints for browsing available restaurants and their offerings

### 🛒 Shopping Cart
- **Dual Cart Support** - Separate cart systems for authenticated users and guest customers
- **Real-Time Quantity Management** - Add, update, and remove items with atomic transactions
- **Price Snapshot** - Preserves item prices at cart time to prevent pricing conflicts
- **Cart Persistence** - Automatic cart recovery for returning users
- **Subtotal Calculation** - Real-time cart value computation

### 📦 Order Management
- **Order Creation** - Checkout flow with tax calculation (8% standard tax)
- **Multiple Payment Methods** - Support for cash and card payments
- **Order Status Tracking** - Comprehensive order lifecycle (Pending → Accepted → Preparing → Ready → Delivered)
- **Order Cancellation** - Customer-initiated order cancellation with state validation
- **Delivery Address Management** - Multiple saved addresses with Home/Work/Other labels
- **Order History** - Complete order records for customers

### 🔔 Real-Time Features
- **WebSocket Order Tracking** - Live order status updates via Django Channels
- **Ping/Pong Connection Monitoring** - Automatic connection health checks
- **Multi-User Order Broadcasting** - Real-time notifications to all connected users for an order

### 📧 Background Tasks
- **Order Confirmation Emails** - Asynchronous email notifications using Celery
- **Task Retry Mechanism** - Automatic retry with exponential backoff (3 retries)
- **Email Queue** - Dedicated Celery queue for email processing
- **Transactional Task Scheduling** - Tasks queued only after successful database commits

### 🌐 Additional Features
- **Geolocation Detection** - Automatic country detection via IP
- **Country & City Management** - Support for international addresses
- **API Caching** - Redis-backed caching for static data (countries list)
- **CORS Support** - Configurable cross-origin requests for frontend integration
- **Rate Limiting** - API throttling to prevent abuse (2 requests/min for anonymous, 4 for authenticated)
- **Django Silk** - Request profiling and debugging interface

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | Django 4.2+ | Backend web framework |
| **API** | Django REST Framework 3.14+ | RESTful API development |
| **Database** | PostgreSQL | Primary data store |
| **Cache/Message Broker** | Redis 4.0+ | Caching and task queue |
| **Task Queue** | Celery 5.2+ | Async job processing |
| **Real-Time** | Django Channels 3.0+ | WebSocket support |
| **ASGI Server** | Daphne 3.0+ | ASGI application server |
| **Authentication** | djangorestframework-simplejwt 5.2+ | JWT token management |
| **Social Auth** | django-allauth 0.50+ | OAuth2 integration |
| **Image Processing** | Pillow 9.0+ | Image uploads and processing |
| **Server** | Gunicorn 20.1+ | WSGI production server |
| **Containerization** | Docker | Application packaging |

## 🏗 Project Architecture

### Application Structure

```
FoodDeliverySystem/
├── config/                 # Django project settings
│   ├── settings.py        # Main configuration
│   ├── urls.py            # URL routing
│   ├── wsgi.py            # WSGI entry point
│   ├── asgi.py            # ASGI entry point (WebSockets)
│   └── celery.py          # Celery configuration
│
├── apps/
│   ├── accounts/          # User authentication & profiles
│   │   ├── models.py      # Profile, EmailOTP
│   │   ├── views/         # Auth, email verification, profile endpoints
│   │   ├── serializers.py # DRF serializers
│   │   └── permissions.py # Custom permission classes
│   │
│   ├── menu/              # Restaurants & menu management
│   │   ├── models.py      # Restaurant, Category, MenuItem
│   │   ├── views.py       # Menu browsing endpoints
│   │   └── serializers.py # Menu serializers
│   │
│   ├── orders/            # Order management & tracking
│   │   ├── models.py      # Order, OrderItem, Address
│   │   ├── views.py       # Order CRUD and tracking
│   │   ├── order_service.py    # Business logic (create, update, cancel)
│   │   ├── tasks.py       # Celery email notifications
│   │   ├── consumers.py   # WebSocket handlers
│   │   ├── routing.py     # WebSocket URL patterns
│   │   └── serializers.py # Order serializers
│   │
│   └── cart/              # Shopping cart functionality
│       ├── models.py      # Cart, CartItem
│       ├── cart_service.py     # Cart operations
│       ├── views.py       # Cart API endpoints
│       └── serializers.py # Cart serializers
│
├── requirements/          # Dependency management
│   ├── base.txt          # Production dependencies
│   ├── dev.txt           # Development & testing
│   └── optional.txt      # Optional features
│
├── templates/            # Django templates
├── static/              # Static files (CSS, JS)
├── media/               # User uploads (avatars, images)
└── Dockerfile           # Container image

```

### Request Flow Architecture

```
┌─────────────────┐
│   Client        │
│  (Web/Mobile)   │
└────────┬────────┘
         │ HTTP/WebSocket
         ↓
┌─────────────────────────────────────┐
│   Nginx/Load Balancer               │
└────────┬────────────────────────────┘
         │
    ┌────┴────┐
    ↓         ↓
┌─────────┐  ┌──────────────┐
│ WSGI    │  │ ASGI/Daphne  │
│Handler  │  │ (WebSocket)  │
└────┬────┘  └──────┬───────┘
     │              │
     ↓              ↓
┌──────────────────────────────┐
│   Django Application         │
│  ┌────────────────────────┐  │
│  │ URL Router             │  │
│  ├─ API Views (DRF)       │  │
│  ├─ WebSocket Consumers   │  │
│  └─ Permission Classes    │  │
│                            │  │
│  Service Layer             │  │
│  ├─ order_service.py       │  │
│  └─ cart_service.py        │  │
└──────┬───────────┬─────────┘
       │           │
       ↓           ↓
┌─────────────┐ ┌────────────────┐
│ PostgreSQL  │ │ Django ORM     │
│ Database    │ │ + Signals      │
└─────────────┘ └────────────────┘

Async Layer:
┌──────────────────┐
│   Redis Broker   │ ← Cache & Message Queue
└──────┬───────────┘
       │
       ↓
┌──────────────────┐
│   Celery Worker  │
│  (Email Tasks)   │
└──────────────────┘
```

### Authentication Flow

```
Registration
    ↓
Create User Account
    ↓
Send Email OTP
    ↓
Verify OTP
    ↓
Account Active
    ↓
User Login
    ↓
Session Created (14 days)
    ↓
API Access Granted
```

## 🔒 Security Considerations

### Implemented Security Measures

#### Authentication & Authorization
- **Session-Based Authentication** - Secure server-side session management with HTTP-only cookies
- **Custom Permission Classes** - `IsManager` permission for role-based access control
- **JWT Support** - Simple JWT integration for token-based authentication
- **Role-Based Access Control** - Four distinct roles with appropriate permissions (Admin, Restaurant, Customer, Delivery)

#### Password Security
- **Django Password Validation** - Multi-layer password strength validation:
  - Minimum length requirements
  - Common password checking
  - User attribute similarity validation
  - Numeric-only password rejection
- **Bcrypt Compatibility** - Support for secure password hashing

#### Data Protection
- **CSRF Protection** - Cross-Site Request Forgery middleware enabled
- **HTTP-Only Cookies** - Session cookies marked as HTTP-only to prevent XSS attacks
- **Secure Session Settings** - 14-day session expiration with automatic browser close cleanup

#### API Security
- **Rate Limiting** - Throttle API requests:
  - Anonymous users: 2 requests/minute
  - Authenticated users: 4 requests/minute
- **CORS Configuration** - Restricted to localhost in development
- **Permission Classes** - All API endpoints require appropriate permissions

#### Environment & Configuration
- **Environment Variables** - Sensitive data stored in `.env` (not in code)
- **Secrets Management** - Django SECRET_KEY externalized from settings
- **DEBUG Mode** - Disabled in production

#### Data Validation
- **Input Validation** - Django serializers validate all incoming requests
- **Email Verification** - OTP-based email confirmation
- **Address Validation** - Django countries library for valid address selection
- **Transaction Integrity** - Database transactions for critical operations

#### WebSocket Security
- **Authenticated Connections** - WebSocket connections require user authentication
- **Order Access Control** - Users can only access their own order updates
- **Connection Validation** - Automatic connection closure for unauthorized access

## 📡 API Overview

### Authentication Endpoints
```
POST   /api/account/register/              - Register new user
POST   /api/account/login/                 - User login
POST   /api/account/logout/                - User logout
POST   /api/account/email/send-otp/        - Send email verification OTP
POST   /api/account/email/verify/          - Verify email with OTP
POST   /api/account/email/resend/          - Resend verification OTP
POST   /api/account/password/reset/        - Request password reset
POST   /api/account/password/reset/verify/ - Verify reset OTP
POST   /api/account/password/reset/new/    - Set new password
```

### Account Management Endpoints
```
GET    /api/account/overview/              - Get account overview
GET    /api/account/personal/              - Get personal information
PUT    /api/account/personal/change-name/  - Update name
PUT    /api/account/personal/change-phone/ - Update phone number
PUT    /api/account/personal/change-email/ - Update email
POST   /api/account/personal/change-avatar/- Upload avatar
PUT    /api/account/personal/change-password/- Change password
```

### Menu & Restaurant Endpoints
```
GET    /api/menu/                          - Get all restaurants and menus
GET    /menu/                              - Menu browsing page
```

### Cart Endpoints
```
GET    /api/v1/cart/                       - Get current cart
POST   /api/v1/cart/add/                   - Add item to cart
PUT    /api/v1/cart/update/                - Update cart item quantity
DELETE /api/v1/cart/remove/                - Remove item from cart
```

### Order Endpoints
```
POST   /api/v1/orders/create/              - Create new order
GET    /api/v1/orders/list/                - List user's orders
GET    /api/v1/orders/<id>/                - Get order details
PUT    /api/v1/orders/<id>/status/         - Update order status
DELETE /api/v1/orders/<id>/cancel/         - Cancel order
```

### Address Endpoints
```
GET    /api/v1/orders/addresses/           - List user addresses
POST   /api/v1/orders/addresses/           - Create new address
GET    /api/v1/orders/address/<id>/        - Get address details
PUT    /api/v1/orders/address/<id>/        - Update address
DELETE /api/v1/orders/address/<id>/        - Delete address
```

### Utility Endpoints
```
GET    /api/v1/orders/countries/           - List all countries (cached)
GET    /api/v1/orders/detect_country/      - Detect user's country via IP
```

### WebSocket Endpoints
```
ws://localhost:8000/ws/orders/<order_id>/ - Order status tracking
```

## 💾 Database Design

### Entity Relationship Diagram

```
┌─────────────────┐         ┌──────────────┐
│ django.auth.User│◄────────┤  Profile     │
├─────────────────┤         ├──────────────┤
│ id (PK)         │  1:1    │ id           │
│ username        │         │ user_id (FK) │
│ email           │         │ role         │
│ password        │         │ avatar       │
│ first_name      │         │ phone        │
│ last_name       │         │ address      │
└─────────────────┘         │ theme        │
                            │ is_verified  │
                            └──────────────┘
        │
        │
        ├──────────────────┬──────────────────┐
        │                  │                  │
        ↓                  ↓                  ↓
    ┌─────────┐      ┌──────────┐      ┌────────────┐
    │   Order │      │ Address  │      │  EmailOTP  │
    ├─────────┤      ├──────────┤      ├────────────┤
    │ id (PK) │      │ id (PK)  │      │ id (PK)    │
    │ user_id │◄─────│ user_id  │      │ user_id    │
    │ address │      │ label    │      │ otp        │
    │ status  │      │ country  │      │ purpose    │
    │ total   │      │ city     │      │ expires_at │
    │ tax     │      │ street   │      └────────────┘
    └────┬────┘      └──────────┘
         │
         │ 1:N
         ↓
    ┌────────────┐
    │ OrderItem  │
    ├────────────┤
    │ id (PK)    │
    │ order_id   │
    │ menu_item  │
    │ quantity   │
    │ price      │
    └────────────┘
         │
         │ FK
         ↓
    ┌─────────────────┐      ┌──────────────┐
    │    MenuItem     │◄─────│  Category    │
    ├─────────────────┤      ├──────────────┤
    │ id (PK)         │      │ id (PK)      │
    │ restaurant_id   │      │ name         │
    │ category_id     │      │ restaurant_id│
    │ name            │      └──────────────┘
    │ price           │
    │ description     │      ┌──────────────┐
    │ img             │◄─────│ Restaurant   │
    │ is_menu         │      ├──────────────┤
    └─────────────────┘      │ id (PK)      │
                             │ name         │
    ┌──────────────────┐     │ logo         │
    │     Cart         │     │ address      │
    ├──────────────────┤     │ phone        │
    │ id (PK)          │     └──────────────┘
    │ user_id (FK)     │
    │ guest_id         │
    │ is_active        │
    └────┬─────────────┘
         │
         │ 1:N
         ↓
    ┌──────────────┐
    │  CartItem    │
    ├──────────────┤
    │ id (PK)      │
    │ cart_id      │
    │ menu_item_id │
    │ quantity     │
    │ price_snap   │
    └──────────────┘
```

### Core Models

- **User** - Django's built-in User model extended with Profile
- **Profile** - User roles, avatar, theme, contact info, verification status
- **EmailOTP** - Time-limited OTP codes for email verification and password reset
- **Restaurant** - Restaurant details with logo and contact information
- **Category** - Menu categories (Drinks, Main Meals, Desserts, Snacks, Salads)
- **MenuItem** - Individual menu items with pricing and images
- **Cart** - Shopping cart for authenticated and guest users
- **CartItem** - Items in a cart with price snapshots
- **Order** - Customer orders with status and payment tracking
- **OrderItem** - Individual items within an order
- **Address** - Delivery addresses with multiple address support

## 📦 Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Redis 6.0+
- pip and virtualenv

### Local Development Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/FoodDeliverySystem.git
cd FoodDeliverySystem
```

#### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements/dev.txt
```

#### 4. Configure Environment Variables

Copy the example environment file and update with your configuration:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Database
DB_NAME=fooddelivery_db
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=your-generated-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email Configuration
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security (Production Only)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

Generate a secure SECRET_KEY:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### 5. Create PostgreSQL Database

```bash
createdb fooddelivery_db
```

#### 6. Run Database Migrations

```bash
python manage.py migrate
```

#### 7. Create Superuser

```bash
python manage.py createsuperuser
```

#### 8. Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

#### 9. Access Django Admin

Visit `http://localhost:8000/admin/` with your superuser credentials

### Additional Setup

#### Redis Server

```bash
# Install Redis (if not already installed)
# macOS
brew install redis

# Windows (via WSL)
sudo apt-get install redis-server

# Start Redis
redis-server
```

#### Celery Worker (for background tasks)

In a separate terminal:

```bash
celery -A config worker -l info
```

#### Django Silk Profiling

View request profiling at `http://localhost:8000/silk/`

## 🐳 Docker Setup

### Build Docker Image

```bash
docker build -t fooddelivery-system:latest .
```

### Run with Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: fooddelivery_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  app:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    environment:
      - DB_NAME=fooddelivery_db
      - DB_USER=postgres
      - DB_PASSWORD=your_secure_password
      - DB_HOST=db
      - REDIS_URL=redis://redis:6379/0
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    volumes:
      - .:/app

  celery:
    build: .
    command: celery -A config worker -l info
    environment:
      - DB_NAME=fooddelivery_db
      - DB_USER=postgres
      - DB_PASSWORD=your_secure_password
      - DB_HOST=db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

### Run Containers

```bash
docker-compose up -d
```

### Access the Application

- API: `http://localhost:8000`
- Django Admin: `http://localhost:8000/admin/`
- Silk Profiling: `http://localhost:8000/silk/`

### Stop Containers

```bash
docker-compose down
```

## ⚙️ Background Tasks with Celery

The system uses Celery for asynchronous job processing with Redis as the message broker.

### Configured Tasks

#### 1. Order Confirmation Email

**Task**: `send_order_confirmation_email`

- **Trigger**: Automatically after successful order creation
- **Retry**: Up to 3 attempts with 60-second intervals
- **Queue**: `emails` queue
- **Transactional**: Queued only after database commit

**Example**:

```python
from apps.orders.tasks import send_order_confirmation_email

# Task is automatically triggered in order_service.py:
order = create_order(user, payment_method, delivery_address_id)
# Email task is queued automatically
```

### Running Celery

```bash
# Single worker
celery -A config worker -l info

# Multiple workers with queues
celery -A config worker -l info -Q emails,default

# Monitor tasks
celery -A config events
```

## 🧪 Testing

The project uses pytest with factory-boy for comprehensive testing.

### Test Structure

```
apps/
├── accounts/tests/        - Authentication and profile tests
├── menu/tests.py          - Menu and restaurant tests
├── orders/tests.py        - Order and order item tests
└── cart/tests.py          - Cart functionality tests
```

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=apps --cov-report=html
```

### Run Specific App Tests

```bash
pytest apps/accounts/tests/
pytest apps/orders/
```

### Run Specific Test Class or Function

```bash
pytest apps/accounts/tests/test_auth.py::TestAuthViews::test_register
```

### Test Configuration

Tests are configured in `pytest.ini`:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
```


## Local Development Setup

### SSL Certificate
```bash
# Generate local self-signed certificate:
.\generate-cert.ps1
```
Certificates will be created in `ssl/` folder. **Do NOT commit these to git.**

### Test Utilities

- **factory-boy**: Model factory fixtures for easy test data creation
- **faker**: Realistic fake data generation
- **pytest-django**: Django-specific pytest plugins
- **pytest-asyncio**: Async test support for WebSocket tests

## 🚀 Future Improvements

### Phase 1: Enhanced Features
- **Real-Time Notifications** - Push notifications to customers on order status changes
- **Analytics Dashboard** - Restaurant revenue, order statistics, and performance metrics
- **Advanced Search** - Full-text menu search with filters and recommendations
- **Favorites System** - Save favorite restaurants and menu items
- **Ratings & Reviews** - Customer reviews and star ratings for restaurants

### Phase 2: Payment Integration
- **Stripe Integration** - Credit/debit card payments with webhook handling
- **Wallet System** - In-app wallet for prepaid orders
- **Multiple Payment Gateways** - Support for local payment providers
- **Refund Management** - Automated refund processing

### Phase 3: Delivery & Logistics
- **Delivery Route Optimization** - AI-based delivery route calculation
- **Driver Tracking** - Real-time GPS tracking for delivery personnel
- **Estimated Delivery Time** - Dynamic ETA calculation
- **Multi-Restaurant Orders** - Combine items from multiple restaurants in one order

### Phase 4: AI & Recommendations
- **Recommendation Engine** - Personalized menu recommendations based on order history
- **Dynamic Pricing** - Surge pricing during peak hours
- **Predictive Analytics** - Forecast demand and optimize inventory

### Phase 5: Operations & Management
- **Inventory Management** - Track menu item availability
- **Restaurant Dashboard** - Real-time order management interface
- **Marketing Tools** - Promotional campaigns and discount codes
- **API Rate Limiting Enhancement** - Flexible tier-based rate limiting

### Technical Improvements
- **GraphQL API** - Alternative to REST API for flexible data querying
- **API Documentation** - Auto-generated API docs with drf-spectacular
- **Monitoring & Logging** - Sentry integration for error tracking
- **Performance Optimization** - Database query optimization and advanced caching strategies
- **Microservices Architecture** - Service separation for scalability

## 📝 License

This project is private/proprietary. All rights reserved.

---

## 👨‍💻 Author

**Created as a production-ready backend system for food delivery platforms**

### Development Stack Highlights
- 🏗️ Modular Django architecture with clear separation of concerns
- 🔐 Enterprise-grade security with role-based access control
- ⚡ Real-time capabilities with WebSocket support
- 🔄 Asynchronous task processing for scalability
- 📊 Comprehensive API with RESTful design principles
- 🧪 Production-ready testing framework
- 🐳 Docker containerization for seamless deployment

---

**Repository**: [FoodDeliverySystem](https://github.com/mrbd17/food-delivery-system)

**Questions or Contributions?** Feel free to reach out or open an issue.
