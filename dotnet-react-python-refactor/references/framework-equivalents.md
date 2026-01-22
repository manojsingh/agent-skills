# .NET to Python Framework Equivalents

This reference provides direct mappings between common .NET patterns and their Python equivalents.

## Web Frameworks

| .NET Framework | Python Equivalent | Notes |
|---------------|-------------------|-------|
| ASP.NET Core MVC | Django | Full-featured, includes ORM, admin |
| ASP.NET Web API | FastAPI | Modern, async, automatic OpenAPI |
| ASP.NET Web API | Flask | Lightweight, flexible |
| ASP.NET SignalR | FastAPI WebSockets | Real-time communication |
| WCF | gRPC-Python | Service-oriented architecture |

## Database & ORM

| .NET Technology | Python Equivalent | Notes |
|----------------|-------------------|-------|
| Entity Framework Core | SQLAlchemy | Most mature Python ORM |
| Entity Framework Core | Django ORM | Integrated with Django |
| Dapper | Records | Lightweight SQL wrapper |
| ADO.NET | psycopg2/asyncpg | Direct database drivers |
| LINQ | SQLAlchemy Query API | Similar query building |

### Entity Framework → SQLAlchemy Patterns

```csharp
// .NET: Querying with LINQ
var users = await context.Users
    .Where(u => u.IsActive)
    .Include(u => u.Profile)
    .OrderBy(u => u.CreatedAt)
    .ToListAsync();
```

```python
# Python: SQLAlchemy equivalent
users = await session.execute(
    select(User)
    .where(User.is_active == True)
    .options(joinedload(User.profile))
    .order_by(User.created_at)
)
users = users.scalars().all()
```

## Dependency Injection

| .NET Pattern | Python Equivalent | Notes |
|-------------|-------------------|-------|
| IServiceCollection | FastAPI Depends() | Built-in DI |
| Constructor Injection | FastAPI Depends() | Function parameters |
| Scoped Services | FastAPI dependency with yield | Cleanup support |
| Singleton Services | Global instances or dependency caching | |

```csharp
// .NET: DI Configuration
services.AddScoped<IProductService, ProductService>();
services.AddSingleton<ICacheService, CacheService>();
```

```python
# Python: FastAPI Dependencies
def get_product_service(db: Session = Depends(get_db)):
    return ProductService(db)

# Singleton pattern
cache_service = CacheService()

def get_cache_service():
    return cache_service
```

## Authentication & Authorization

| .NET Technology | Python Equivalent | Notes |
|----------------|-------------------|-------|
| ASP.NET Identity | Django Auth | Built-in user management |
| JWT Authentication | python-jose | JWT encoding/decoding |
| OAuth2 | Authlib | OAuth2 client/server |
| Claims-based Auth | FastAPI Security | Role-based access |
| [Authorize] Attribute | FastAPI Depends(get_current_user) | Route protection |

```csharp
// .NET: JWT Authentication
[Authorize(Roles = "Admin")]
[HttpGet("admin")]
public IActionResult AdminOnly() { }
```

```python
# Python: FastAPI equivalent
@router.get("/admin")
async def admin_only(user = Depends(get_current_admin_user)):
    pass

async def get_current_admin_user(user = Depends(get_current_user)):
    if "Admin" not in user.roles:
        raise HTTPException(status_code=403)
    return user
```

## Validation

| .NET Technology | Python Equivalent | Notes |
|----------------|-------------------|-------|
| Data Annotations | Pydantic | Model validation |
| FluentValidation | Pydantic validators | Custom validation |
| ModelState | Pydantic ValidationError | Automatic validation |

```csharp
// .NET: Data Annotations
public class CreateUserDto
{
    [Required]
    [StringLength(100)]
    public string Name { get; set; }
    
    [EmailAddress]
    public string Email { get; set; }
    
    [Range(18, 100)]
    public int Age { get; set; }
}
```

```python
# Python: Pydantic equivalent
from pydantic import BaseModel, EmailStr, Field, validator

class CreateUserDto(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=18, le=100)
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v
```

## HTTP Client

| .NET Technology | Python Equivalent | Notes |
|----------------|-------------------|-------|
| HttpClient | httpx | Async HTTP client |
| HttpClient | requests | Sync HTTP client |
| RestSharp | httpx | REST client |

```csharp
// .NET: HTTP Client
var response = await httpClient.GetAsync("https://api.example.com/users");
var users = await response.Content.ReadAsAsync<List<User>>();
```

```python
# Python: httpx equivalent
async with httpx.AsyncClient() as client:
    response = await client.get("https://api.example.com/users")
    users = response.json()
```

## Caching

| .NET Technology | Python Equivalent | Notes |
|----------------|-------------------|-------|
| IMemoryCache | cachetools | In-memory caching |
| IDistributedCache (Redis) | redis-py | Redis integration |
| [ResponseCache] | fastapi-cache2 | Response caching |

```csharp
// .NET: Memory Cache
var cachedValue = await cache.GetOrCreateAsync("key", async entry =>
{
    entry.AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(5);
    return await GetExpensiveData();
});
```

```python
# Python: cachetools equivalent
from cachetools import TTLCache
import asyncio

cache = TTLCache(maxsize=100, ttl=300)

async def get_cached_data(key: str):
    if key in cache:
        return cache[key]
    
    data = await get_expensive_data()
    cache[key] = data
    return data
```

## Background Jobs

| .NET Technology | Python Equivalent | Notes |
|----------------|-------------------|-------|
| Hangfire | Celery | Distributed task queue |
| Quartz.NET | APScheduler | Job scheduling |
| BackgroundService | asyncio tasks | Simple background tasks |
| IHostedService | FastAPI startup events | Lifecycle management |

```csharp
// .NET: Background Service
public class EmailService : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken token)
    {
        while (!token.IsCancellationRequested)
        {
            await SendPendingEmails();
            await Task.Delay(TimeSpan.FromMinutes(5), token);
        }
    }
}
```

```python
# Python: Celery task
from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379')

@app.task
def send_pending_emails():
    # Send emails
    pass

# Schedule periodic task
from celery.schedules import crontab

app.conf.beat_schedule = {
    'send-emails-every-5-minutes': {
        'task': 'tasks.send_pending_emails',
        'schedule': 300.0,  # 5 minutes
    },
}
```

## Configuration

| .NET Technology | Python Equivalent | Notes |
|----------------|-------------------|-------|
| appsettings.json | python-dotenv | Environment variables |
| IConfiguration | pydantic Settings | Type-safe config |
| User Secrets | python-dotenv | Development secrets |

```csharp
// .NET: Configuration
public class AppSettings
{
    public string ConnectionString { get; set; }
    public string ApiKey { get; set; }
}

// appsettings.json
{
    "ConnectionString": "...",
    "ApiKey": "..."
}
```

```python
# Python: Pydantic Settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    connection_string: str
    api_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Logging

| .NET Technology | Python Equivalent | Notes |
|----------------|-------------------|-------|
| ILogger | logging module | Built-in Python logging |
| Serilog | structlog | Structured logging |
| Application Insights | OpenTelemetry | Observability |

```csharp
// .NET: Logging
_logger.LogInformation("Processing request {RequestId}", requestId);
_logger.LogError(ex, "Error processing request");
```

```python
# Python: logging equivalent
import logging

logger = logging.getLogger(__name__)
logger.info("Processing request %s", request_id)
logger.error("Error processing request", exc_info=True)
```

## Serialization

| .NET Technology | Python Equivalent | Notes |
|----------------|-------------------|-------|
| System.Text.Json | json (built-in) | Standard JSON |
| Newtonsoft.Json | orjson | Fast JSON library |
| XML Serialization | lxml | XML processing |

```csharp
// .NET: JSON Serialization
var json = JsonSerializer.Serialize(user);
var user = JsonSerializer.Deserialize<User>(json);
```

```python
# Python: JSON equivalent
import json

json_str = json.dumps(user.__dict__)
user_data = json.loads(json_str)
```

## Testing

| .NET Technology | Python Equivalent | Notes |
|----------------|-------------------|-------|
| xUnit | pytest | Popular testing framework |
| NUnit | unittest | Built-in testing |
| Moq | unittest.mock | Mocking library |
| FluentAssertions | pytest assertions | Assertion library |

```csharp
// .NET: xUnit Test
[Fact]
public async Task GetUser_ReturnsUser()
{
    var result = await _service.GetUserAsync(1);
    Assert.NotNull(result);
    Assert.Equal("John", result.Name);
}
```

```python
# Python: pytest equivalent
@pytest.mark.asyncio
async def test_get_user_returns_user():
    result = await service.get_user(1)
    assert result is not None
    assert result.name == "John"
```

## Data Types

| C# Type | Python Type | Notes |
|---------|-------------|-------|
| int | int | Integer |
| long | int | Python int has unlimited precision |
| float | float | Floating point |
| decimal | Decimal | For precise decimals |
| string | str | String |
| bool | bool | Boolean |
| DateTime | datetime | Date and time |
| TimeSpan | timedelta | Time duration |
| Guid | UUID | Unique identifier |
| byte[] | bytes | Byte array |
| List<T> | list[T] | List/Array |
| Dictionary<K,V> | dict[K, V] | Dictionary/Map |
| HashSet<T> | set[T] | Set |
| Task<T> | Awaitable[T] | Async result |

## Common Nuget → PyPI Packages

| NuGet Package | PyPI Package | Purpose |
|--------------|--------------|---------|
| Newtonsoft.Json | orjson | Fast JSON |
| Serilog | structlog | Structured logging |
| AutoMapper | pydantic | Object mapping |
| Polly | tenacity | Retry/resilience |
| MediatR | N/A | Use DI directly |
| FluentValidation | pydantic | Validation |
| Swagger/Swashbuckle | FastAPI built-in | API docs |
| StackExchange.Redis | redis-py | Redis client |
| Npgsql | asyncpg | PostgreSQL |
| Dapper | records | Lightweight ORM |

## Performance Equivalents

| .NET Feature | Python Equivalent | Notes |
|-------------|-------------------|-------|
| async/await | async/await | Similar syntax |
| Parallel.ForEach | asyncio.gather | Concurrent execution |
| Task.Run | asyncio.create_task | Background execution |
| CancellationToken | asyncio.Task.cancel | Task cancellation |
| ValueTask | N/A | Use regular coroutines |

## Migration Checklist

When migrating specific .NET features:

1. **Controllers** → FastAPI routers (similar structure)
2. **Services** → Python service classes (same pattern)
3. **Models** → Pydantic/SQLAlchemy models
4. **DTOs** → Pydantic schemas
5. **Middleware** → FastAPI middleware
6. **Filters** → FastAPI dependencies/middleware
7. **Action Results** → FastAPI Response models
8. **Model Binding** → Pydantic automatic parsing
9. **Routing** → FastAPI routing decorators
10. **CORS** → FastAPI CORS middleware

## Common Gotchas

### Null Handling
- C#: `string?` (nullable reference types)
- Python: `Optional[str]` from typing module

### Property Access
- C#: `user.Name` (property)
- Python: `user.name` (attribute) - convention is snake_case

### Async Conventions
- C#: `async Task<T>` methods
- Python: `async def` functions returning `T`

### Exception Handling
- C#: Try-catch blocks work similarly
- Python: Try-except blocks (similar syntax)

### Interface Implementation
- C#: Explicit interfaces
- Python: Duck typing or ABC (Abstract Base Classes)
