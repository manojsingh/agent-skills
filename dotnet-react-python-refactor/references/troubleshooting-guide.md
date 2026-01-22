# Comprehensive Troubleshooting Guide

Troubleshooting common issues when migrating from .NET to React + Python stack.

## Table of Contents

1. [Database Issues](#database-issues)
2. [Authentication & Authorization](#authentication--authorization)
3. [API & Network Issues](#api--network-issues)
4. [Frontend Issues](#frontend-issues)
5. [Docker & Container Issues](#docker--container-issues)
6. [Performance Problems](#performance-problems)
7. [Deployment Issues](#deployment-issues)
8. [Migration-Specific Issues](#migration-specific-issues)

---

## Database Issues

### Issue: Database Connection Fails

**Symptoms:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Diagnosis:**
```bash
# Check if database is running
docker-compose ps postgres

# Test connection manually
psql -h localhost -U myuser -d mydb

# Check database logs
docker-compose logs postgres
```

**Solutions:**

1. **Verify DATABASE_URL format:**
   ```python
   # Correct format
   DATABASE_URL = "postgresql://user:password@host:5432/dbname"
   
   # Common mistakes:
   # - Missing port: postgresql://user:password@host/dbname
   # - Wrong scheme: postgres:// vs postgresql://
   # - Special characters in password not URL-encoded
   ```

2. **Check network connectivity:**
   ```bash
   # From backend container
   docker-compose exec backend ping postgres
   
   # Check if port is accessible
   telnet postgres 5432
   ```

3. **Firewall/Security group:**
   - Ensure port 5432 is open
   - Check AWS security group rules
   - Verify Docker network configuration

4. **Wait for database to be ready:**
   ```python
   # Add health check in docker-compose.yml
   postgres:
     healthcheck:
       test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
       interval: 10s
       timeout: 5s
       retries: 5
   
   backend:
     depends_on:
       postgres:
         condition: service_healthy
   ```

### Issue: N+1 Query Problem

**Symptoms:**
- Slow API responses
- Too many database queries
- High database CPU usage

**Diagnosis:**
```python
# Enable SQLAlchemy query logging
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

**Solutions:**

1. **Use eager loading:**
   ```python
   # BAD - Causes N+1 queries
   users = session.query(User).all()
   for user in users:
       print(user.posts)  # Separate query for each user
   
   # GOOD - Single query with join
   from sqlalchemy.orm import joinedload
   users = session.query(User).options(joinedload(User.posts)).all()
   ```

2. **Use select_related for foreign keys:**
   ```python
   # Django ORM
   posts = Post.objects.select_related('author').all()
   
   # SQLAlchemy
   posts = session.query(Post).join(Post.author).all()
   ```

3. **Implement pagination:**
   ```python
   from fastapi import Query
   
   @app.get("/api/posts")
   def get_posts(skip: int = Query(0), limit: int = Query(10)):
       return db.query(Post).offset(skip).limit(limit).all()
   ```

### Issue: Migration Fails

**Symptoms:**
```
alembic.util.exc.CommandError: Can't locate revision identified by 'abc123'
```

**Solutions:**

1. **Reset migrations (dev only):**
   ```bash
   # Drop all tables
   docker-compose exec backend alembic downgrade base
   
   # Delete migration files
   rm alembic/versions/*.py
   
   # Generate new migration
   alembic revision --autogenerate -m "initial"
   alembic upgrade head
   ```

2. **Fix migration conflicts:**
   ```bash
   # Check current version
   alembic current
   
   # Manually edit migration file to resolve conflicts
   # Then run
   alembic upgrade head
   ```

3. **For production:**
   ```bash
   # Backup database first!
   pg_dump mydb > backup.sql
   
   # Then carefully apply migrations
   alembic upgrade head
   ```

### Issue: Transaction Deadlocks

**Symptoms:**
```
psycopg2.extensions.TransactionRollbackError: deadlock detected
```

**Solutions:**

1. **Keep transactions short:**
   ```python
   # BAD - Long transaction
   with db.begin():
       user = db.query(User).get(1)
       time.sleep(5)  # Don't do this!
       user.name = "New Name"
   
   # GOOD - Quick transaction
   with db.begin():
       user = db.query(User).get(1)
       user.name = "New Name"
   ```

2. **Consistent lock ordering:**
   ```python
   # Always acquire locks in same order
   # BAD - Different order can cause deadlock
   with db.begin():
       user1 = db.query(User).with_for_update().get(1)
       user2 = db.query(User).with_for_update().get(2)
   
   # Somewhere else:
   with db.begin():
       user2 = db.query(User).with_for_update().get(2)
       user1 = db.query(User).with_for_update().get(1)  # Deadlock!
   
   # GOOD - Always same order (by ID)
   ids = sorted([user1_id, user2_id])
   users = db.query(User).with_for_update().filter(User.id.in_(ids)).all()
   ```

---

## Authentication & Authorization

### Issue: JWT Token Not Working

**Symptoms:**
```
401 Unauthorized
"Could not validate credentials"
```

**Diagnosis:**
```bash
# Decode JWT token (jwt.io or)
python -c "import jwt; print(jwt.decode('YOUR_TOKEN', options={'verify_signature': False}))"
```

**Solutions:**

1. **Check token format:**
   ```python
   # Ensure token is sent as Bearer token
   headers = {
       "Authorization": f"Bearer {token}"  # Must include "Bearer "
   }
   ```

2. **Verify secret key:**
   ```python
   # Ensure same SECRET_KEY is used for encoding and decoding
   # Check environment variables
   import os
   print(os.getenv('SECRET_KEY'))
   ```

3. **Check token expiration:**
   ```python
   from datetime import datetime, timedelta
   
   # Increase expiration for testing
   ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Instead of 30
   ```

4. **CORS issues with credentials:**
   ```python
   # Backend - allow credentials
   app.add_middleware(
       CORSMiddleware,
       allow_credentials=True,  # Must be True
       allow_origins=["http://localhost:3000"],  # Specific origins
   )
   
   # Frontend - include credentials
   fetch('/api/endpoint', {
       credentials: 'include',  # Important!
   })
   ```

### Issue: CORS Errors

**Symptoms:**
```
Access to fetch at 'http://localhost:8000/api/users' from origin 'http://localhost:3000' 
has been blocked by CORS policy
```

**Solutions:**

1. **Configure FastAPI CORS:**
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "http://localhost:3000",
           "http://127.0.0.1:3000",
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Check preflight requests:**
   ```python
   # Ensure OPTIONS requests are handled
   @app.options("/{path:path}")
   async def options_handler(path: str):
       return {"message": "OK"}
   ```

3. **Nginx configuration:**
   ```nginx
   location /api/ {
       # Add CORS headers
       add_header Access-Control-Allow-Origin $http_origin always;
       add_header Access-Control-Allow-Credentials true always;
       add_header Access-Control-Allow-Methods 'GET, POST, PUT, DELETE, OPTIONS' always;
       add_header Access-Control-Allow-Headers 'Authorization, Content-Type' always;
       
       if ($request_method = 'OPTIONS') {
           return 204;
       }
       
       proxy_pass http://backend;
   }
   ```

### Issue: Session Not Persisting

**Symptoms:**
- User gets logged out immediately
- Session data disappears

**Solutions:**

1. **Check Redis connection:**
   ```bash
   # Test Redis
   docker-compose exec redis redis-cli ping
   # Should return PONG
   ```

2. **Verify session configuration:**
   ```python
   from fastapi import FastAPI
   from starlette.middleware.sessions import SessionMiddleware
   
   app = FastAPI()
   app.add_middleware(
       SessionMiddleware,
       secret_key="your-secret-key",
       max_age=3600,  # 1 hour
       same_site="lax",
       https_only=False,  # Set to True in production with HTTPS
   )
   ```

3. **Check cookie settings:**
   ```javascript
   // Frontend - ensure cookies are sent
   axios.defaults.withCredentials = true;
   
   // Or with fetch
   fetch('/api/endpoint', {
       credentials: 'include'
   })
   ```

---

## API & Network Issues

### Issue: API Returns 500 Internal Server Error

**Diagnosis:**
```bash
# Check backend logs
docker-compose logs -f backend

# Enable debug mode temporarily
export DEBUG=True
uvicorn app.main:app --reload
```

**Solutions:**

1. **Add proper error handling:**
   ```python
   from fastapi import HTTPException
   
   @app.get("/api/users/{user_id}")
   async def get_user(user_id: int):
       try:
           user = db.query(User).filter(User.id == user_id).first()
           if not user:
               raise HTTPException(status_code=404, detail="User not found")
           return user
       except Exception as e:
           logger.error(f"Error fetching user: {e}")
           raise HTTPException(status_code=500, detail="Internal server error")
   ```

2. **Check request validation:**
   ```python
   from pydantic import BaseModel, validator
   
   class UserCreate(BaseModel):
       email: str
       age: int
       
       @validator('age')
       def validate_age(cls, v):
           if v < 0 or v > 150:
               raise ValueError('Invalid age')
           return v
   ```

### Issue: Slow API Response Times

**Diagnosis:**
```python
# Add timing middleware
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"{request.url.path}: {process_time:.2f}s")
    return response
```

**Solutions:**

1. **Add database indexing:**
   ```python
   # SQLAlchemy
   class User(Base):
       __tablename__ = "users"
       
       email = Column(String, unique=True, index=True)  # Add index
       created_at = Column(DateTime, index=True)  # Index for sorting
   ```

2. **Implement caching:**
   ```python
   from functools import lru_cache
   import redis
   
   redis_client = redis.Redis(host='redis', port=6379)
   
   @app.get("/api/users/{user_id}")
   async def get_user(user_id: int):
       # Check cache first
       cached = redis_client.get(f"user:{user_id}")
       if cached:
           return json.loads(cached)
       
       # Fetch from database
       user = db.query(User).get(user_id)
       
       # Cache result
       redis_client.setex(
           f"user:{user_id}",
           3600,  # 1 hour
           json.dumps(user.dict())
       )
       
       return user
   ```

3. **Use async database operations:**
   ```python
   from databases import Database
   
   database = Database("postgresql://...")
   
   @app.get("/api/users")
   async def get_users():
       query = "SELECT * FROM users"
       return await database.fetch_all(query)
   ```

### Issue: Request Timeout

**Symptoms:**
```
TimeoutError: Request timeout
```

**Solutions:**

1. **Increase timeout limits:**
   ```python
   # Uvicorn
   uvicorn app.main:app --timeout-keep-alive 60
   
   # Nginx
   # In nginx.conf
   proxy_read_timeout 300;
   proxy_connect_timeout 300;
   proxy_send_timeout 300;
   ```

2. **For long-running tasks, use background jobs:**
   ```python
   from fastapi import BackgroundTasks
   
   def process_data(data):
       # Long-running task
       time.sleep(60)
   
   @app.post("/api/process")
   async def process_endpoint(background_tasks: BackgroundTasks, data: dict):
       background_tasks.add_task(process_data, data)
       return {"message": "Processing started"}
   ```

---

## Frontend Issues

### Issue: React App Shows Blank Page

**Diagnosis:**
```bash
# Check browser console for errors
# F12 -> Console tab

# Check if build exists
ls -la frontend/dist/

# Check frontend logs
docker-compose logs frontend
```

**Solutions:**

1. **Check routing configuration:**
   ```jsx
   // App.jsx
   import { BrowserRouter } from 'react-router-dom';
   
   function App() {
       return (
           <BrowserRouter>
               <Routes>
                   <Route path="/" element={<Home />} />
                   {/* other routes */}
               </Routes>
           </BrowserRouter>
       );
   }
   ```

2. **Verify API URL:**
   ```javascript
   // .env or config.js
   const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
   console.log('API URL:', API_URL);  // Debug
   ```

3. **Check build configuration:**
   ```javascript
   // vite.config.js
   export default {
       server: {
           port: 3000,
           host: '0.0.0.0'
       },
       build: {
           outDir: 'dist'
       }
   }
   ```

### Issue: API Calls Failing from Frontend

**Diagnosis:**
```javascript
// Add error logging
axios.interceptors.response.use(
    response => response,
    error => {
        console.error('API Error:', error.response?.data);
        console.error('Status:', error.response?.status);
        console.error('Headers:', error.response?.headers);
        return Promise.reject(error);
    }
);
```

**Solutions:**

1. **Check network tab:** F12 -> Network
   - Is request being made?
   - What's the response code?
   - Check request headers

2. **Verify axios configuration:**
   ```javascript
   import axios from 'axios';
   
   const api = axios.create({
       baseURL: process.env.REACT_APP_API_URL,
       withCredentials: true,
       headers: {
           'Content-Type': 'application/json'
       }
   });
   
   // Add auth token
   api.interceptors.request.use(config => {
       const token = localStorage.getItem('token');
       if (token) {
           config.headers.Authorization = `Bearer ${token}`;
       }
       return config;
   });
   ```

### Issue: React State Not Updating

**Symptoms:**
- UI doesn't reflect state changes
- Components not re-rendering

**Solutions:**

1. **Use proper state updates:**
   ```jsx
   // BAD - Mutating state directly
   const [user, setUser] = useState({ name: 'John' });
   user.name = 'Jane';  // Don't do this!
   
   // GOOD - Create new object
   setUser({ ...user, name: 'Jane' });
   
   // For arrays
   // BAD
   items.push(newItem);  // Don't do this!
   
   // GOOD
   setItems([...items, newItem]);
   ```

2. **Check useEffect dependencies:**
   ```jsx
   // BAD - Missing dependencies
   useEffect(() => {
       fetchUser(userId);
   }, []);  // userId should be in deps!
   
   // GOOD
   useEffect(() => {
       fetchUser(userId);
   }, [userId]);  // Re-run when userId changes
   ```

---

## Docker & Container Issues

### Issue: Container Exits Immediately

**Diagnosis:**
```bash
# Check container logs
docker-compose logs backend

# Check container status
docker-compose ps

# Inspect container
docker inspect container_id
```

**Solutions:**

1. **Check for syntax errors:**
   ```bash
   # Test Python syntax
   docker-compose run backend python -m py_compile app/main.py
   ```

2. **Verify entrypoint:**
   ```dockerfile
   # Ensure correct command in Dockerfile
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

3. **Check dependencies:**
   ```bash
   # Rebuild without cache
   docker-compose build --no-cache backend
   ```

### Issue: Out of Disk Space

**Symptoms:**
```
no space left on device
```

**Solutions:**
```bash
# Remove unused containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Check disk usage
docker system df

# Clean everything (CAUTION!)
docker system prune -a --volumes
```

### Issue: Port Already in Use

**Symptoms:**
```
Error: bind: address already in use
```

**Solutions:**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 PID

# Or use different port in docker-compose.yml
ports:
  - "8001:8000"
```

---

## Performance Problems

### Issue: High Memory Usage

**Diagnosis:**
```bash
# Check container stats
docker stats

# Check memory usage
docker-compose exec backend python -c "import psutil; print(psutil.virtual_memory())"
```

**Solutions:**

1. **Set memory limits:**
   ```yaml
   # docker-compose.yml
   services:
     backend:
       deploy:
         resources:
           limits:
             memory: 512M
   ```

2. **Optimize queries:**
   ```python
   # Use pagination
   @app.get("/api/users")
   def get_users(skip: int = 0, limit: int = 100):
       return db.query(User).offset(skip).limit(limit).all()
   ```

3. **Clean up connections:**
   ```python
   # Use connection pooling
   engine = create_engine(
       DATABASE_URL,
       pool_size=5,
       max_overflow=10,
       pool_recycle=3600
   )
   ```

### Issue: Slow Docker Build

**Solutions:**

1. **Use multi-stage builds:**
   ```dockerfile
   FROM python:3.11-slim as builder
   COPY requirements.txt .
   RUN pip install --user -r requirements.txt
   
   FROM python:3.11-slim
   COPY --from=builder /root/.local /root/.local
   COPY . .
   ```

2. **Optimize layer caching:**
   ```dockerfile
   # Copy requirements first (changes less often)
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   # Copy code last (changes more often)
   COPY . .
   ```

3. **Use .dockerignore:**
   ```
   .git
   __pycache__
   *.pyc
   node_modules
   .env
   .vscode
   ```

---

## Deployment Issues

### Issue: SSL Certificate Errors

**Solutions:**

1. **Let's Encrypt certificate:**
   ```bash
   # Install certbot
   sudo apt-get install certbot python3-certbot-nginx
   
   # Get certificate
   sudo certbot --nginx -d yourdomain.com
   
   # Test renewal
   sudo certbot renew --dry-run
   ```

2. **Update nginx config:**
   ```nginx
   server {
       listen 443 ssl http2;
       ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
   }
   ```

### Issue: Environment Variables Not Loading

**Solutions:**

1. **Check .env file:**
   ```bash
   # Verify file exists
   ls -la .env
   
   # Check format (no spaces around =)
   DATABASE_URL=postgresql://...  # Correct
   # DATABASE_URL = postgresql://...  # Wrong!
   ```

2. **Load in Docker Compose:**
   ```yaml
   services:
     backend:
       env_file:
         - .env
       # Or explicitly
       environment:
         - DATABASE_URL=${DATABASE_URL}
   ```

---

## Migration-Specific Issues

### Issue: Date/Time Handling Differences

**Problem:** .NET and Python handle timezones differently

**Solutions:**

1. **Always use UTC:**
   ```python
   from datetime import datetime, timezone
   
   # Store in UTC
   now = datetime.now(timezone.utc)
   
   # Convert for display
   local_time = now.astimezone()
   ```

2. **Consistent date formatting:**
   ```python
   # ISO 8601 format
   date_str = datetime.now().isoformat()
   ```

### Issue: Decimal/Money Precision

**Problem:** Financial calculations lose precision

**Solutions:**

1. **Use Decimal type:**
   ```python
   from decimal import Decimal
   from sqlalchemy import Numeric
   
   class Product(Base):
       price = Column(Numeric(10, 2))  # 10 digits, 2 decimal places
   
   # In calculations
   price = Decimal('19.99')
   tax = Decimal('0.08')
   total = price * (1 + tax)
   ```

### Issue: Entity Framework to SQLAlchemy Mapping

**Problem:** EF conventions don't translate directly

**Solutions:**

1. **Manual table naming:**
   ```python
   class User(Base):
       __tablename__ = 'Users'  # Match EF convention if needed
   ```

2. **Handle navigation properties:**
   ```python
   # EF: user.Posts (collection)
   # SQLAlchemy:
   class User(Base):
       posts = relationship("Post", back_populates="author")
   
   class Post(Base):
       author_id = Column(Integer, ForeignKey('users.id'))
       author = relationship("User", back_populates="posts")
   ```

---

## Getting More Help

### Enable Debug Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# SQLAlchemy queries
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# HTTP requests
logging.getLogger('uvicorn.access').setLevel(logging.DEBUG)
```

### Useful Commands

```bash
# Check all logs
docker-compose logs -f --tail=100

# Execute commands in container
docker-compose exec backend bash

# Check database
docker-compose exec postgres psql -U user -d dbname

# Test API endpoints
curl -X GET http://localhost:8000/api/health -v

# Monitor resources
docker stats

# Network debugging
docker network ls
docker network inspect network_name
```

### When to Ask for Help

- Persistent errors after trying solutions
- Security-related issues
- Data corruption or loss
- Performance degradation in production
- Complex migration scenarios

Provide:
- Error messages and stack traces
- Relevant configuration files
- Steps to reproduce
- What you've already tried
