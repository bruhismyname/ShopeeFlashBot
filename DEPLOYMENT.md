# Deployment Guide - ShopeeFlashBot SaaS

This guide explains how to deploy the ShopeeFlashBot SaaS platform.

## Prerequisites

### System Requirements
- Python 3.9 or higher
- Chrome/Chromium browser
- Redis server (for background tasks)
- PostgreSQL or MySQL (recommended for production)

### Development Environment
- Ubuntu/Debian Linux or macOS recommended
- Windows with WSL2 also supported

## Installation Steps

### 1. Clone Repository
```bash
git clone https://github.com/bruhismyname/ShopeeFlashBot.git
cd ShopeeFlashBot
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Chrome and ChromeDriver

#### Ubuntu/Debian
```bash
# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb

# ChromeDriver will be automatically managed by undetected-chromedriver
```

#### macOS
```bash
brew install --cask google-chrome
```

### 5. Install Redis

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

#### macOS
```bash
brew install redis
brew services start redis
```

### 6. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
nano .env
```

**Important**: Change the `SECRET_KEY` in production!

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 7. Database Setup

#### Option A: SQLite (Development)
No additional setup needed. Database file will be created automatically.

#### Option B: PostgreSQL (Production)
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE shopee_saas;
CREATE USER shopee_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE shopee_saas TO shopee_user;
\q

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://shopee_user:your_password@localhost:5432/shopee_saas
```

## Running the Application

### Development Mode

#### Start API Server
```bash
python -m saas.app
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

#### Start Background Worker (Optional)
For background task processing:
```bash
celery -A saas.services.tasks worker --loglevel=info
```

### Production Mode

#### Using Uvicorn
```bash
uvicorn saas.app:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Using Gunicorn (Recommended)
```bash
pip install gunicorn
gunicorn saas.app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Docker Deployment

### Build Docker Image
```dockerfile
# Dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "saas.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/shopee_saas
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./saas:/app/saas

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=shopee_saas
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  worker:
    build: .
    command: celery -A saas.services.tasks worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/shopee_saas
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

### Run with Docker Compose
```bash
docker-compose up -d
```

## Nginx Reverse Proxy

### Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## Systemd Service

Create a systemd service for automatic startup:

```ini
# /etc/systemd/system/shopee-saas.service
[Unit]
Description=ShopeeFlashBot SaaS API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ShopeeFlashBot
Environment="PATH=/opt/ShopeeFlashBot/venv/bin"
ExecStart=/opt/ShopeeFlashBot/venv/bin/uvicorn saas.app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable shopee-saas
sudo systemctl start shopee-saas
sudo systemctl status shopee-saas
```

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### View Logs
```bash
# Systemd logs
sudo journalctl -u shopee-saas -f

# Docker logs
docker-compose logs -f api
```

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use strong database passwords
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall (ufw/iptables)
- [ ] Set up rate limiting
- [ ] Enable CORS properly
- [ ] Regular security updates
- [ ] Backup database regularly

## Troubleshooting

### Chrome/ChromeDriver Issues
```bash
# Check Chrome version
google-chrome --version

# Test Chrome headless
google-chrome --headless --disable-gpu --dump-dom https://google.com
```

### Redis Connection Issues
```bash
# Test Redis connection
redis-cli ping
# Should return: PONG
```

### Database Connection Issues
```bash
# Test PostgreSQL connection
psql -U shopee_user -d shopee_saas -h localhost
```

## Performance Tuning

### Uvicorn Workers
Adjust based on CPU cores:
```bash
uvicorn saas.app:app --workers $((2 * $(nproc) + 1))
```

### Database Connection Pool
For high traffic, configure connection pooling in settings.

### Redis Optimization
```bash
# Edit /etc/redis/redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
```

## Backup Strategy

### Database Backup
```bash
# PostgreSQL backup
pg_dump -U shopee_user shopee_saas > backup_$(date +%Y%m%d).sql

# Restore
psql -U shopee_user shopee_saas < backup_20231215.sql
```

### Automated Backups
```bash
# Cron job (add to crontab)
0 2 * * * /opt/scripts/backup_database.sh
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/bruhismyname/ShopeeFlashBot/issues
- Email: muflihul.aufa@gmail.com

## License

MIT License - See LICENSE file for details
