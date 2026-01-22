# .NET to React + Python Refactor Skill - Usage Guide

## Overview

This comprehensive agent skill guides the systematic refactoring of .NET applications into a modern React frontend with Python backend architecture. The skill includes detailed workflows, reference materials, utility scripts, and templates.

## Skill Contents

```
dotnet-to-react-python-refactor/
├── SKILL.md                                    # Main skill instructions
├── references/                                  # Detailed reference documentation
│   ├── architecture-patterns.md                # Architecture patterns for different .NET app types
│   ├── framework-equivalents.md                # Quick-reference .NET to Python mappings
│   ├── orm-migration.md                        # Entity Framework to SQLAlchemy/Django ORM mapping
│   ├── authentication-patterns.md              # Authentication migration patterns
│   ├── api-integration.md                      # React-Python API integration patterns
│   └── testing-strategies.md                   # Comprehensive testing approaches
├── scripts/                                     # Utility scripts
│   ├── assess_dotnet_app.py                    # Analyze .NET projects
│   └── init_python_backend.py                  # Initialize Python backend projects
└── assets/                                      # Templates and resources
    ├── docker-compose.yml                      # Full-stack Docker setup
    ├── .env.example                            # Environment variables template
    └── react-project-template/                 # React project structure guide
        └── README.md
```

## Quick Start Guide

### Step 1: Assessment

First, assess your existing .NET application:

```bash
python scripts/assess_dotnet_app.py /path/to/dotnet/project -o assessment.json
```

This generates a comprehensive migration inventory including:
- Controllers and routes
- Models and database entities
- Views and UI components
- Services and business logic
- Dependencies and their Python equivalents
- Authentication mechanisms
- Migration recommendations

### Step 2: Backend Migration

Initialize your new Python backend:

```bash
# FastAPI (recommended for most projects)
python scripts/init_python_backend.py my-api --framework fastapi --db-type postgresql

# Or Flask for simpler APIs
python scripts/init_python_backend.py my-api --framework flask --db-type postgresql

# Or Django for full-featured applications
python scripts/init_python_backend.py my-api --framework django --db-type postgresql
```

This creates a complete project structure with:
- Database configuration
- API routing setup
- Authentication scaffolding
- Sample models and endpoints
- Docker configuration
- Testing setup

### Step 3: Frontend Setup

Create your React frontend:

```bash
# Using Vite (recommended)
npm create vite@latest frontend -- --template react

# Or Create React App
npx create-react-app frontend
```

Follow the structure outlined in `assets/react-project-template/README.md`.

### Step 4: Follow Migration Workflow

Use the main SKILL.md as your guide through the 6-phase migration process:

1. **Assessment and Architecture Planning**
2. **Backend Migration (.NET → Python)**
3. **Frontend Migration (.NET Views → React)**
4. **Data Layer Migration**
5. **Testing and Validation**
6. **Deployment Strategy**

## Reference Documentation

### Architecture Patterns (`references/architecture-patterns.md`)

Consult this when:
- Planning your target architecture
- Migrating different .NET application types (MVC, Web API, Web Forms, Blazor)
- Choosing between monolithic or microservices architecture
- Designing API gateway patterns
- Selecting appropriate technology stack

**Key Topics:**
- ASP.NET MVC → React + Python
- Web API → Python REST API
- Web Forms → Modern SPA
- Blazor → React
- Database architecture patterns
- State management architectures
- Deployment architectures

### Framework Equivalents (`references/framework-equivalents.md`)

Consult this when:
- Looking for quick Python equivalents of .NET technologies
- Migrating specific NuGet packages to PyPI packages
- Converting .NET patterns (DI, caching, logging, etc.) to Python
- Understanding data type mappings
- Checking common gotchas and pitfalls

**Key Topics:**
- Web framework comparisons
- Dependency injection patterns
- Validation (Pydantic vs Data Annotations)
- HTTP client equivalents
- Caching implementations
- Background jobs (Hangfire → Celery)
- Configuration patterns
- Logging equivalents
- NuGet to PyPI package mappings
- Data type conversions
- Common migration gotchas

### ORM Migration (`references/orm-migration.md`)

Consult this when:
- Migrating Entity Framework models to SQLAlchemy or Django ORM
- Converting LINQ queries to Python
- Handling relationships and constraints
- Implementing repository patterns
- Dealing with transactions and migrations

**Key Topics:**
- Model mapping (EF → SQLAlchemy/Django)
- Query translation (LINQ → Python)
- Relationships (one-to-many, many-to-many)
- Data annotations and constraints
- Lazy vs eager loading
- Common ORM patterns

### Authentication Patterns (`references/authentication-patterns.md`)

Consult this when:
- Migrating ASP.NET Identity to JWT-based auth
- Implementing authentication in Python backend
- Setting up protected routes in React
- Handling token refresh and storage
- Implementing role-based authorization

**Key Topics:**
- JWT token-based authentication
- Session-based alternatives
- Frontend integration (React)
- Role-based authorization
- OAuth2 and social login
- Security best practices

### API Integration (`references/api-integration.md`)

Consult this when:
- Connecting React frontend to Python backend
- Setting up API client layer
- Implementing error handling
- Working with file uploads
- Adding pagination
- Using WebSockets

**Key Topics:**
- React Query (TanStack Query) integration
- Axios setup and interceptors
- Error handling patterns
- File upload implementation
- Pagination strategies
- WebSocket integration
- API versioning

### Testing Strategies (`references/testing-strategies.md`)

Consult this when:
- Setting up testing infrastructure
- Writing unit tests for Python backend
- Testing React components
- Implementing E2E tests
- Ensuring test coverage

**Key Topics:**
- Python backend testing (pytest)
- React component testing (Jest, RTL)
- Integration testing
- End-to-end testing (Cypress)
- Test coverage requirements
- Testing best practices

## Utility Scripts

### assess_dotnet_app.py

**Purpose**: Analyze .NET applications and generate migration inventories

**Usage**:
```bash
python scripts/assess_dotnet_app.py <project-path> [-o output-file.json]
```

**Output**: JSON report containing:
- Project type detection
- Controllers, models, views inventory
- Route mapping
- Database context analysis
- Dependency analysis with Python equivalents
- Migration recommendations

**Example**:
```bash
python scripts/assess_dotnet_app.py ./MyDotNetApp -o migration-plan.json
```

### init_python_backend.py

**Purpose**: Scaffold Python backend project with chosen framework

**Usage**:
```bash
python scripts/init_python_backend.py <project-name> \
  --framework [fastapi|flask|django] \
  --db-type [postgresql|mysql|sqlite]
```

**Creates**:
- Complete project structure
- Database configuration
- Sample models and endpoints
- Authentication scaffolding
- Docker setup
- Testing infrastructure
- Requirements.txt

**Example**:
```bash
python scripts/init_python_backend.py my-ecommerce-api \
  --framework fastapi \
  --db-type postgresql
```

## Assets

The skill includes ready-to-use asset files that you can copy to your projects.

### docker-compose.yml

**Location:** `assets/docker-compose.yml`

**Purpose:** Production-ready Docker Compose configuration for full-stack deployment

**What it includes:**
- **PostgreSQL database** with health checks and volume persistence
- **Redis cache** for session storage and caching
- **FastAPI backend** with hot-reload for development
- **React frontend** container with Vite
- **Nginx reverse proxy** for production mode

**Usage:**
```bash
# Copy to your project root
cp assets/docker-compose.yml /path/to/your/project/

# Start all services (development)
docker-compose up -d

# Start with production profile (includes Nginx)
docker-compose --profile production up -d

# View logs
docker-compose logs -f backend
```

**When to use:** Phase 6 (Deployment) or during local development

---

### .env.example

**Location:** `assets/.env.example`

**Purpose:** Template for environment variables

**Usage:**
```bash
# Copy to backend directory
cp assets/.env.example /path/to/backend/.env

# Edit with your actual values
nano /path/to/backend/.env
```

**Important:** Never commit `.env` files to version control. Change `SECRET_KEY` in production.

**When to use:** Phase 2 (Backend Migration) - during initial setup

---

### react-project-template/

**Location:** `assets/react-project-template/README.md`

**Purpose:** React project structure guide with recommended setup and dependencies

**When to use:** Phase 3 (Frontend Migration) - when setting up React project

## Common Migration Patterns

### Pattern 1: ASP.NET MVC → React + FastAPI

1. Run assessment script
2. Initialize FastAPI backend
3. Migrate business logic to Python services
4. Convert Entity Framework models to SQLAlchemy
5. Create React components from Razor views
6. Implement API endpoints for each controller
7. Connect frontend to backend via React Query

### Pattern 2: Web API → React + Python

1. Map existing API routes to Python framework
2. Convert DTOs to Pydantic models (FastAPI) or Marshmallow (Flask)
3. Reimplement business logic in Python
4. Build React frontend consuming the API
5. Ensure API contract compatibility

### Pattern 3: Incremental Migration (Strangler Fig)

1. Start with backend API migration
2. Create proxy layer to route between old and new systems
3. Migrate features incrementally
4. Build React components as backend endpoints are ready
5. Gradually replace old system

## Best Practices

1. **Always assess first**: Use the assessment script to understand your application
2. **Start with backend**: Migrate business logic and API before frontend
3. **Test continuously**: Write tests as you migrate, don't wait until the end
4. **Keep documentation**: Document architectural decisions and migration notes
5. **Incremental approach**: For large apps, use strangler fig pattern
6. **Monitor performance**: Profile database queries and API endpoints
7. **Security first**: Implement authentication and authorization early
8. **Code quality**: Follow PEP 8 (Python) and ESLint rules (React)

## Troubleshooting

### Common Issues

**Issue**: Database connection fails
- Check DATABASE_URL environment variable
- Verify database service is running
- Check firewall/network settings

**Issue**: CORS errors in React app
- Configure CORS in backend (see authentication-patterns.md)
- Verify allowed origins match frontend URL

**Issue**: Authentication token not persisting
- Check token storage implementation
- Verify interceptors are configured correctly

**Issue**: N+1 query problems
- Use eager loading (see orm-migration.md)
- Profile database queries
- Implement proper relationship loading

## Additional Resources

- **Python FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://react.dev/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **React Query Documentation**: https://tanstack.com/query/latest

## Support

For issues or questions:
1. Review the relevant reference documentation
2. Check the testing strategies for validation approaches
3. Consult the architecture patterns for design guidance
4. Use the scripts to automate common tasks

## License

See individual files for licensing information.
