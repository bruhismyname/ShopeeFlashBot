# ShopeeFlashBot SaaS Architecture

## Overview

ShopeeFlashBot has been transformed from a single-user script into a multi-tenant Software as a Service (SaaS) platform. This document describes the architecture, features, and implementation details.

## Architecture Components

### 1. API Layer (`saas/api/`)

The API layer provides RESTful endpoints for user management and bot operations.

#### Authentication (`auth.py`)
- User registration and login
- JWT-based authentication
- Password hashing with bcrypt
- Token-based authorization

#### Bot Tasks (`bot_tasks.py`)
- Create, read, update, delete bot tasks
- Start/stop bot instances
- Task status monitoring
- Subscription tier-based limits

### 2. Models (`saas/models/`)

Data models using Pydantic for validation and serialization.

#### User Model (`user.py`)
- User profile information
- Subscription tier management
- Authentication credentials

#### Bot Task Model (`bot_task.py`)
- Task configuration and scheduling
- Status tracking (pending, running, completed, failed)
- Error logging and reporting

### 3. Services (`saas/services/`)

Business logic layer for bot execution.

#### Bot Service (`bot_service.py`)
- Selenium-based browser automation
- Headless Chrome for scalability
- Purchase flow execution
- Multiple bot instance management

### 4. Configuration (`saas/config/`)

Application settings and environment configuration.

#### Settings (`settings.py`)
- Database configuration
- API settings
- Subscription tiers definition
- Security settings

## Features

### Multi-Tenancy
- User isolation with separate sessions
- Per-user task management
- Subscription-based resource limits

### Subscription Tiers

| Tier | Max Bots | Max Schedules | Priority | Price |
|------|----------|---------------|----------|-------|
| Free | 1 | 5 | 3 | $0 |
| Basic | 3 | 20 | 2 | $9.99/mo |
| Premium | 10 | 100 | 1 | $29.99/mo |

### Bot Automation
- Scheduled flash sale purchases
- Configurable product options
- Multiple payment methods support
- Automatic retry mechanisms
- Error handling and logging

### API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token
- `GET /api/v1/auth/me` - Get current user info

#### Bot Tasks
- `POST /api/v1/tasks` - Create new task
- `GET /api/v1/tasks` - List user's tasks
- `GET /api/v1/tasks/{id}` - Get task details
- `POST /api/v1/tasks/{id}/run` - Execute task
- `POST /api/v1/tasks/{id}/cancel` - Cancel running task
- `DELETE /api/v1/tasks/{id}` - Delete task

## Technology Stack

### Backend
- **FastAPI** - Modern, high-performance web framework
- **Pydantic** - Data validation and serialization
- **JWT** - Authentication tokens
- **Bcrypt** - Password hashing

### Automation
- **Selenium** - Browser automation
- **Undetected ChromeDriver** - Bot detection bypass
- **Headless Chrome** - Scalable browser instances

### Infrastructure
- **Celery + Redis** - Task queue for background jobs
- **SQLite/PostgreSQL** - Database (configurable)
- **Docker** - Containerization (optional)

## Security Features

1. **Authentication & Authorization**
   - JWT-based token authentication
   - Password hashing with bcrypt
   - Per-user resource isolation

2. **Rate Limiting**
   - Subscription tier-based limits
   - Task concurrency controls
   - API request throttling

3. **Data Protection**
   - Environment-based secrets
   - Secure credential storage
   - User data isolation

## Scalability Considerations

### Horizontal Scaling
- Stateless API design
- Background task distribution
- Load balancing support

### Resource Management
- Headless browser mode
- Concurrent bot instance limits
- Task queue prioritization

### Performance Optimization
- Async/await patterns
- Background task processing
- Database query optimization

## Deployment

### Requirements
- Python 3.9+
- Chrome/Chromium browser
- Redis server (for task queue)
- PostgreSQL/MySQL (production)

### Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=your-secret-key
API_PORT=8000
REDIS_URL=redis://localhost:6379/0
```

### Running the Service
```bash
# Install dependencies
pip install -r requirements.txt

# Run API server
python -m saas.app

# Run Celery worker (for background tasks)
celery -A saas.services.tasks worker --loglevel=info
```

## API Usage Example

### 1. Register a User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepassword"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

### 3. Create Bot Task
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "name": "Flash Sale Product",
    "url": "https://shopee.co.id/...",
    "target_time": "00:00:00",
    "config": {
      "product_option": "Red",
      "payment_method": "ShopeePay",
      "use_voucher": true
    }
  }'
```

### 4. Run Task
```bash
curl -X POST http://localhost:8000/api/v1/tasks/1/run \
  -H "Authorization: Bearer <your-token>"
```

## Future Enhancements

1. **Database Integration**
   - SQLAlchemy ORM
   - PostgreSQL/MySQL support
   - Database migrations

2. **Frontend Dashboard**
   - React/Vue.js web interface
   - Real-time task monitoring
   - User management UI

3. **Payment Integration**
   - Stripe/PayPal integration
   - Subscription management
   - Billing automation

4. **Advanced Features**
   - Webhook notifications
   - Email alerts
   - Analytics dashboard
   - Multi-region support

5. **Monitoring & Logging**
   - Application metrics
   - Error tracking (Sentry)
   - Performance monitoring
   - Audit logs

## Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guide
- Tests cover new functionality
- Documentation is updated
- Security best practices are followed

## License

This project is licensed under the MIT License.

## Disclaimer

This SaaS platform is for educational purposes. Automated purchasing may violate Shopee's terms of service. Users are responsible for compliance with applicable laws and platform policies.
