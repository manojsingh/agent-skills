# .NET to React + Python Refactor Skill - Usage Guide

## Overview

This comprehensive agent skill guides the systematic refactoring of .NET applications into a modern React frontend with Python backend architecture. The skill includes detailed workflows, reference materials, utility scripts, and templates.

## Skill Contents

```
dotnet-to-react-python-refactor/
├── SKILL.md                                    # Main skill instructions
├── USAGE_GUIDE.md                              # This file - comprehensive usage guide
├── references/                                  # Detailed reference documentation
│   ├── architecture-patterns.md                # Architecture patterns for different .NET app types
│   ├── framework-equivalents.md                # Quick-reference .NET to Python mappings
│   ├── orm-migration.md                        # Entity Framework to SQLAlchemy/Django ORM mapping
│   ├── authentication-patterns.md              # Authentication migration patterns
│   ├── api-integration.md                      # React-Python API integration patterns
│   ├── testing-strategies.md                   # Comprehensive testing approaches
│   ├── security-hardening-checklist.md         # Security best practices and checklist
│   ├── troubleshooting-guide.md                # Comprehensive troubleshooting solutions
│   └── deployment-guides/                      # Deployment guides for various platforms
│       ├── docker-compose-deployment.md        # Docker Compose deployment
│       └── aws-deployment.md                   # AWS deployment (EC2, ECS, Elastic Beanstalk)
├── scripts/                                     # Utility scripts
│   ├── assess_dotnet_app.py                    # Analyze .NET projects
│   ├── init_python_backend.py                  # Initialize Python backend projects
│   ├── generate_migration.py                   # Generate database migrations from .NET models
│   └── convert_razor_to_jsx.py                 # Convert Razor views to React JSX components
└── assets/                                      # Templates and resources
    ├── docker-compose.yml                      # Full-stack Docker setup
    ├── .env.example                            # Environment variables template
    ├── nginx.conf                              # Nginx reverse proxy configuration
    ├── Dockerfile.dev                          # Development Dockerfile for frontend
    ├── react-project-template/                 # React project structure guide
    │   └── README.md
    ├── react-component-templates/              # Ready-to-use React component templates
    │   ├── README.md                           # Component usage guide
    │   ├── Button.jsx                          # Button component
    │   ├── Button.css                          # Button styles
    │   ├── Input.jsx                           # Input component with validation
    │   ├── Input.css                           # Input styles
    │   ├── Modal.jsx                           # Modal dialog component
    │   └── Modal.css                           # Modal styles
    └── cicd-templates/                         # CI/CD pipeline templates
        ├── README.md                           # CI/CD setup guide
        ├── github-actions.yml                  # GitHub Actions workflow
        └── gitlab-ci.yml                       # GitLab CI/CD pipeline
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

### Security Hardening Checklist (`references/security-hardening-checklist.md`)

Consult this when:
- Preparing for production deployment
- Conducting security audits
- Implementing authentication and authorization
- Securing Docker containers and infrastructure
- Setting up monitoring and incident response

**Key Topics:**
- Application security best practices
- Backend API security (input validation, rate limiting, SQL injection prevention)
- Frontend security (XSS prevention, CSRF protection, secure token storage)
- Database security (encrypted connections, access control, backup encryption)
- Infrastructure security (Docker best practices, secrets management)
- Authentication & authorization (JWT token security, password hashing)
- Network security (HTTPS, security headers, CORS configuration)
- Monitoring and incident response

### Troubleshooting Guide (`references/troubleshooting-guide.md`)

Consult this when:
- Encountering errors during migration or deployment
- Debugging database connection issues
- Solving authentication problems
- Fixing API and network issues
- Resolving Docker container problems
- Addressing performance issues

**Key Topics:**
- Database issues (connection failures, N+1 queries, migration failures, deadlocks)
- Authentication & authorization (JWT tokens, CORS errors, session persistence)
- API & network issues (500 errors, slow responses, timeouts)
- Frontend issues (blank pages, API call failures, state updates)
- Docker & container issues (container exits, disk space, port conflicts)
- Performance problems (high memory usage, slow builds)
- Deployment issues (SSL certificates, environment variables)
- Migration-specific issues (date/time handling, decimal precision, EF to SQLAlchemy mapping)

### Deployment Guides (`references/deployment-guides/`)

#### Docker Compose Deployment (`docker-compose-deployment.md`)

**When to use:** Development, staging, and small-scale production deployments

**Covers:**
- Complete deployment architecture
- Configuration files (Dockerfile, docker-compose.yml, .env)
- Development and production deployment workflows
- Database management and backups
- Monitoring and logging
- Scaling services
- Performance optimization
- Zero-downtime updates
- Security best practices

**Steps:**
1. Project structure setup
2. Configuration files
3. Development deployment
4. Production deployment (with SSL/HTTPS)
5. Database management and backups
6. Monitoring and logging
7. Scaling strategies
8. Performance optimization
9. Updates and maintenance



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

### generate_migration.py

**Purpose**: Generate Python ORM models and database migrations from .NET Entity Framework models

**Usage**:
```bash
python scripts/generate_migration.py <path-to-dotnet-models> \
  --framework [sqlalchemy|django] \
  --output ./migrations
```

**Features**:
- Parses C# model files (.cs)
- Extracts properties, data annotations, and relationships
- Maps C# types to Python/SQLAlchemy types
- Generates SQLAlchemy or Django ORM models
- Creates migration guide with step-by-step instructions
- Handles Entity Framework conventions

**Output**:
- `models.py` - Complete ORM models
- `MIGRATION_GUIDE.md` - Instructions for applying migrations

**Example**:
```bash
# Generate SQLAlchemy models
python scripts/generate_migration.py ./dotnet-app/Models \
  --framework sqlalchemy \
  --output ./backend/migrations

# Generate Django models
python scripts/generate_migration.py ./dotnet-app/Models \
  --framework django \
  --output ./backend/myapp
```

**When to use:** Phase 4 (Data Layer Migration) after analyzing existing .NET models

### convert_razor_to_jsx.py

**Purpose**: Convert ASP.NET Razor views to React JSX components

**Usage**:
```bash
# Convert single file
python scripts/convert_razor_to_jsx.py path/to/view.cshtml --output ./converted

# Convert entire directory
python scripts/convert_razor_to_jsx.py ./Views --output ./frontend/src/components
```

**Features**:
- Converts Razor syntax to JSX
- Transforms HTML helpers to React components
- Converts tag helpers to JSX equivalents
- Handles @if/@foreach statements
- Generates React component boilerplate
- Includes state management and event handlers
- Produces conversion report with TODOs

**Conversions Handled**:
- `@Model.Property` → `{props.property}`
- `@Html.ActionLink` → `<a href="...">`
- `@Html.TextBoxFor` → `<Input>` component
- `@if` conditions → Ternary operators
- `@foreach` loops → `.map()` iterations
- Tag helpers → JSX equivalents
- `class` → `className`
- `for` → `htmlFor`

**Output**:
- `.jsx` files for each converted view
- `CONVERSION_REPORT.md` - Summary and manual review items

**Example**:
```bash
python scripts/convert_razor_to_jsx.py ./Views/Home/Index.cshtml
```

**When to use:** Phase 3 (Frontend Migration) when converting Razor views to React

**Note:** This is semi-automated. Manual review and adjustments are required for:
- Complex business logic
- Form submission handlers
- Client-side validation
- Nested component structure
- State management integration

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

---

### nginx.conf

**Location:** `assets/nginx.conf`

**Purpose:** Production-ready Nginx reverse proxy configuration

**Features:**
- Reverse proxy for API requests to backend
- Static file serving for React frontend
- CORS header configuration
- WebSocket support
- SSL/HTTPS configuration (commented, ready for production)
- Security headers
- Gzip compression
- Health check endpoint

**Usage:**
```bash
# Copy to project root
cp assets/nginx.conf /path/to/your/project/

# Use in docker-compose.yml
volumes:
  - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
```

**When to use:** Phase 6 (Deployment) - production deployments with Nginx

---

### Dockerfile.dev

**Location:** `assets/Dockerfile.dev`

**Purpose:** Development Dockerfile for React frontend with hot-reload

**Features:**
- Based on Node.js Alpine image
- npm dependencies cached
- Hot-reload enabled
- Configured for Vite, CRA, or Next.js

**Usage:**
```bash
# Copy to frontend directory
cp assets/Dockerfile.dev /path/to/frontend/

# Use in docker-compose.yml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile.dev
```

**When to use:** Phase 3 (Frontend Migration) - Docker-based development environment

---

### React Component Templates

**Location:** `assets/react-component-templates/`

**Purpose:** Production-ready React component templates

**Available Components:**
- **Button.jsx** - Flexible button with variants (primary, secondary, danger, success, outline) and sizes
- **Input.jsx** - Form input with label, validation, error display, and accessibility
- **Modal.jsx** - Modal dialog with overlay, animations, and keyboard support

**Features:**
- Full TypeScript/PropTypes support
- Accessibility (ARIA attributes, keyboard navigation)
- CSS included with each component
- Customizable and extensible
- Production-ready code quality

**Usage:**
```bash
# Copy components to your project
cp -r assets/react-component-templates/* /path/to/frontend/src/components/

# Import and use
import Button from './components/Button';
import Input from './components/Input';
import Modal from './components/Modal';
```

**When to use:** Phase 3 (Frontend Migration) - as building blocks for converted Razor views

**See also:** `assets/react-component-templates/README.md` for detailed usage examples and customization guide

---

### CI/CD Pipeline Templates

**Location:** `assets/cicd-templates/`

**Purpose:** Ready-to-use CI/CD pipeline configurations

**Available Templates:**
1. **github-actions.yml** - GitHub Actions workflow
2. **gitlab-ci.yml** - GitLab CI/CD pipeline

**Features:**
- Backend testing (Python, pytest, flake8, mypy)
- Frontend testing (Node.js, Jest, ESLint, TypeScript)
- Code coverage reporting (Codecov)
- Security scanning (Snyk, Trivy)
- Docker image building and publishing
- Automated deployment to staging/production
- E2E testing with Playwright
- Notifications (Slack)

**Usage:**
```bash
# For GitHub Actions
mkdir -p .github/workflows
cp assets/cicd-templates/github-actions.yml .github/workflows/ci-cd.yml

# For GitLab CI
cp assets/cicd-templates/gitlab-ci.yml .gitlab-ci.yml
```

**Setup Requirements:**
- Configure repository secrets (API tokens, SSH keys, credentials)
- Customize deployment targets and environments
- Adjust test commands for your project structure

**When to use:** After Phase 5 (Testing) - to automate build, test, and deployment processes

**See also:** `assets/cicd-templates/README.md` for detailed setup instructions and customization guide

---

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
