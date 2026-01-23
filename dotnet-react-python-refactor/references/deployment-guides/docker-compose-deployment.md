# Docker Compose Deployment Guide

This guide covers deploying your React + Python application using Docker Compose, suitable for development, staging, and small-scale production deployments.

## Prerequisites

- Docker 20.10+ installed
- Docker Compose 2.0+ installed
- Domain name configured (for production)
- SSL certificates (for production HTTPS)

## Deployment Architecture

```
┌─────────────────────────────────────────────────┐
│               Nginx (Port 80/443)               │
│         (Reverse Proxy & Static Files)          │
└─────────────┬───────────────────────────────────┘
              │
      ┌───────┴────────┐
      │                │
      ▼                ▼
┌──────────┐    ┌──────────────┐
│  React   │    │   FastAPI    │
│ Frontend │    │   Backend    │
│ (Port    │    │  (Port 8000) │
│  3000)   │    │              │
└──────────┘    └───────┬──────┘
                        │
                ┌───────┴──────┐
                │              │
                ▼              ▼
          ┌──────────┐   ┌─────────┐
          │PostgreSQL│   │  Redis  │
          │ (Port    │   │ (Port   │
          │  5432)   │   │  6379)  │
          └──────────┘   └─────────┘
```

## Step 1: Project Structure

Ensure your project structure looks like this:

```
project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models/
│   │   ├── routes/
│   │   └── ...
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── Dockerfile
│   └── Dockerfile.dev
├── docker-compose.yml
├── nginx.conf
└── .env.example
```

## Step 2: Configuration Files

### Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile (Production)

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Environment Variables

Create `.env` file in project root:

```bash
# Database
POSTGRES_USER=myapp_user
POSTGRES_PASSWORD=secure_password_here
POSTGRES_DB=myapp_db
DATABASE_URL=postgresql://myapp_user:secure_password_here@postgres:5432/myapp_db

# Redis
REDIS_URL=redis://redis:6379/0

# Backend
SECRET_KEY=your_secret_key_here_min_32_chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# Frontend
REACT_APP_API_URL=http://localhost:80/api
REACT_APP_ENV=production
```

### Docker Compose File

Use the provided `docker-compose.yml` from assets directory, or create:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    env_file:
      - .env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev  # Use Dockerfile for production
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - REACT_APP_API_URL=http://localhost/api
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./frontend/dist:/usr/share/nginx/html:ro  # Production build
      # - ./ssl:/etc/nginx/ssl:ro  # For HTTPS
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
    profiles:
      - production

volumes:
  postgres_data:
  redis_data:
```

## Step 3: Development Deployment

### Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432

### Common Commands

```bash
# Stop services
docker-compose down

# Stop and remove volumes (CAUTION: deletes data)
docker-compose down -v

# Rebuild after code changes
docker-compose build

# Restart a specific service
docker-compose restart backend

# Execute command in container
docker-compose exec backend python manage.py migrate
docker-compose exec postgres psql -U myapp_user -d myapp_db

# View logs for specific service
docker-compose logs -f backend
```

## Step 4: Production Deployment

### Build Production Images

```bash
# Build frontend production bundle
cd frontend
npm run build
cd ..

# Build all images
docker-compose build --no-cache

# Start with production profile (includes Nginx)
docker-compose --profile production up -d
```

### Production Checklist

- [ ] Change all default passwords in `.env`
- [ ] Generate secure `SECRET_KEY` (32+ random characters)
- [ ] Configure proper `BACKEND_CORS_ORIGINS`
- [ ] Set up SSL certificates
- [ ] Configure proper domain names
- [ ] Set up automated backups for PostgreSQL
- [ ] Configure log rotation
- [ ] Set up monitoring (Prometheus, Grafana)
- [ ] Configure firewall rules
- [ ] Enable HTTPS in nginx.conf
- [ ] Set up health checks
- [ ] Configure resource limits in docker-compose.yml

### SSL/HTTPS Configuration

1. **Obtain SSL Certificates** (Let's Encrypt example):

```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Certificates will be in /etc/letsencrypt/live/yourdomain.com/
```

2. **Update docker-compose.yml** volumes:

```yaml
nginx:
  volumes:
    - /etc/letsencrypt:/etc/letsencrypt:ro
```

3. **Update nginx.conf** (uncomment HTTPS server block)

4. **Set up certificate renewal**:

```bash
# Add to crontab
0 0 * * * certbot renew --quiet && docker-compose restart nginx
```

## Step 5: Database Management

### Initial Setup

```bash
# Create database tables
docker-compose exec backend alembic upgrade head

# Or for Django
docker-compose exec backend python manage.py migrate
```

### Backup Database

```bash
# Create backup
docker-compose exec postgres pg_dump -U myapp_user myapp_db > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U myapp_user myapp_db < backup.sql
```

### Automated Backups

Create `backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="backup_$DATE.sql"

docker-compose exec -T postgres pg_dump -U myapp_user myapp_db > "$BACKUP_DIR/$FILENAME"

# Compress backup
gzip "$BACKUP_DIR/$FILENAME"

# Delete backups older than 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
```

Add to crontab:

```bash
0 2 * * * /path/to/backup.sh
```

## Step 6: Monitoring and Logging

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service with tail
docker-compose logs -f --tail=100 backend

# Export logs
docker-compose logs > app.log
```

### Log Rotation

Create `/etc/logrotate.d/docker-compose`:

```
/var/lib/docker/containers/*/*.log {
  rotate 7
  daily
  compress
  missingok
  delaycompress
  copytruncate
}
```

### Health Checks

Test health endpoints:

```bash
# Backend health
curl http://localhost/api/health

# Check service health
docker-compose ps
```

## Step 7: Scaling

### Scale Services

```bash
# Scale backend to 3 instances
docker-compose up -d --scale backend=3

# Nginx will load balance automatically
```

### Update docker-compose.yml for better scaling:

```yaml
backend:
  deploy:
    replicas: 3
    resources:
      limits:
        cpus: '0.5'
        memory: 512M
      reservations:
        cpus: '0.25'
        memory: 256M
```

## Step 8: Performance Optimization

### Enable Production Mode

1. **Backend**: Set `DEBUG=False`
2. **Frontend**: Use production build
3. **Database**: Tune PostgreSQL settings
4. **Redis**: Configure persistence

### Database Optimization

Add to docker-compose.yml postgres service:

```yaml
postgres:
  command: >
    postgres
    -c max_connections=200
    -c shared_buffers=256MB
    -c effective_cache_size=1GB
    -c maintenance_work_mem=64MB
    -c checkpoint_completion_target=0.9
```

## Step 9: Updates and Maintenance

### Zero-Downtime Updates

```bash
# 1. Build new image
docker-compose build backend

# 2. Scale up with new version
docker-compose up -d --scale backend=2 --no-recreate

# 3. Test new instance
# ...

# 4. Remove old instances
docker-compose up -d --scale backend=1
```

### Rollback

```bash
# Use previous image
docker-compose down
docker-compose up -d --force-recreate
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs backend

# Check if port is in use
lsof -i :8000

# Restart service
docker-compose restart backend
```

### Database Connection Issues

```bash
# Test connection
docker-compose exec backend python -c "from app.database import engine; print(engine.connect())"

# Check PostgreSQL logs
docker-compose logs postgres
```

### Out of Memory

```bash
# Check container stats
docker stats

# Increase memory in docker-compose.yml
backend:
  deploy:
    resources:
      limits:
        memory: 1G
```

## Security Best Practices

1. **Never commit `.env` files** - Use `.env.example` templates
2. **Use strong passwords** - Generate with `openssl rand -base64 32`
3. **Limit exposed ports** - Only expose necessary ports
4. **Update images regularly** - `docker-compose pull && docker-compose up -d`
5. **Use secrets management** - Docker secrets or external vault
6. **Enable firewall** - UFW or iptables
7. **Regular backups** - Automated daily backups
8. **Monitor logs** - Set up log aggregation
9. **Security scanning** - Use `docker scan`
10. **Network isolation** - Use Docker networks

## Production Checklist

- [ ] All services start successfully
- [ ] Database migrations applied
- [ ] SSL/HTTPS configured
- [ ] CORS properly configured
- [ ] Backups automated
- [ ] Monitoring set up
- [ ] Logs rotating properly
- [ ] Health checks working
- [ ] Resource limits set
- [ ] Security scanning passed
- [ ] Load testing completed
- [ ] Rollback procedure tested
- [ ] Documentation updated

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)
- [Nginx Docker](https://hub.docker.com/_/nginx)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/docker/)

## Support

For issues specific to your deployment:
1. Check service logs: `docker-compose logs`
2. Verify configurations in `.env`
3. Test network connectivity between services
4. Review nginx access/error logs
5. Check resource usage: `docker stats`
