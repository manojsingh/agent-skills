---
name: dotnet-to-react-python-refactor
description: Comprehensive agent skill for refactoring .NET applications into a modern React frontend and Python backend architecture. Use when users request to migrate, refactor, or modernize .NET applications to a React + Python stack, or when analyzing .NET codebases for migration planning. Handles full-stack migration including backend API conversion, frontend rewrite, data layer migration, authentication, and deployment strategy.
---

# .NET to React + Python Refactor Agent

This skill guides the systematic refactoring of .NET applications into a React frontend with Python backend architecture.

## Core Workflow

### Phase 1: Assessment and Architecture Planning

**1. Analyze Current .NET Application**

Examine the existing codebase structure:
- Identify application type (ASP.NET MVC, Web Forms, Web API, Blazor, etc.)
- Map controllers, models, views, and data access layers
- Document external dependencies and integrations
- Identify authentication/authorization mechanisms
- List database connections and ORM usage (Entity Framework, Dapper, etc.)
- Note third-party packages and their Python/React equivalents

Run the assessment script to generate a migration inventory:
```bash
python scripts/assess_dotnet_app.py /path/to/dotnet/project
```

**2. Design Target Architecture**

Define the new architecture based on assessment results:
- **Frontend**: React SPA with routing, state management, and UI framework
- **Backend**: Python REST API (FastAPI/Flask/Django) with appropriate ORM
- **Data Layer**: Database migration strategy (same DB or migration required)
- **Authentication**: JWT, OAuth2, or session-based approach
- **API Contract**: RESTful design with clear endpoint mapping

Create an architecture document (use references/architecture-patterns.md for guidance).

### Phase 2: Backend Migration (.NET → Python)

**1. Set Up Python Backend Framework**

Choose framework based on application complexity:
- **FastAPI**: Modern async API, automatic OpenAPI docs, high performance
- **Flask**: Lightweight, flexible, good for simple to medium APIs
- **Django REST Framework**: Full-featured, includes ORM and admin panel

Initialize project structure:
```bash
python scripts/init_python_backend.py --framework fastapi --db-type postgresql
```

**2. Migrate Business Logic**

Convert .NET controllers and services to Python:

a. **Map Routes and Endpoints**
   - Document all .NET controller routes
   - Design equivalent REST endpoints
   - Consider RESTful conventions and resource naming

b. **Convert Business Logic**
   - Translate C# classes to Python classes
   - Convert LINQ queries to Python list comprehensions or database queries
   - Handle async/await patterns appropriately
   - Replace .NET-specific types with Python equivalents

c. **Data Access Layer Migration**
   - Map Entity Framework models to SQLAlchemy/Django ORM models
   - Convert database queries and stored procedures
   - Implement repository pattern if used in original
   - Consider references/orm-migration.md for detailed ORM patterns

**3. Implement API Endpoints**

For each .NET controller action, create corresponding Python endpoint:
- Match HTTP methods (GET, POST, PUT, DELETE)
- Implement request/response DTOs with Pydantic (FastAPI) or dataclasses
- Add input validation and error handling
- Include proper status codes and error messages

**4. Authentication and Authorization**

Convert .NET authentication to Python equivalent:
- Map ASP.NET Identity to JWT tokens or session-based auth
- Implement role-based or policy-based authorization
- Migrate user management and password hashing
- See references/authentication-patterns.md for implementation patterns

### Phase 3: Frontend Migration (.NET Views → React)

**1. Initialize React Application**

Choose setup based on requirements:
```bash
# For modern React with build tools
npx create-react-app frontend
# Or for production-ready setup with routing
npx create-next-app frontend
# Or use Vite for faster development
npm create vite@latest frontend -- --template react-ts
```

Configure project structure using assets/react-project-template/ as reference.

**2. Component Extraction and Migration**

Convert .NET views to React components:

a. **Identify View Hierarchy**
   - Map Razor views/pages to React component structure
   - Identify reusable partial views as React components
   - Plan component composition and prop flow

b. **Convert Markup**
   - Transform Razor syntax to JSX
   - Convert server-side logic to client-side state management
   - Replace HTML helpers with React component libraries
   - Update form handling from server-side to client-side validation

c. **State Management**
   - Choose state management approach (Context API, Redux, Zustand)
   - Convert ViewBag/ViewData/TempData to component state or global state
   - Implement client-side caching strategies for API data

**3. Routing and Navigation**

Replace ASP.NET routing with React Router:
- Map route definitions from .NET to React Router
- Implement protected routes for authenticated pages
- Add navigation components (headers, menus, breadcrumbs)
- Handle deep linking and browser history

**4. API Integration**

Connect React frontend to Python backend:
- Create API client layer (axios, fetch, or React Query)
- Implement request/response interceptors for auth tokens
- Add loading states and error handling
- Consider references/api-integration.md for patterns

**5. Forms and Validation**

Migrate form handling:
- Use form libraries (React Hook Form, Formik) for complex forms
- Implement client-side validation matching backend rules
- Convert .NET ModelState to React validation patterns
- Add proper error display and user feedback

### Phase 4: Data Layer Migration

**1. Database Schema Review**

Assess database migration needs:
- Review existing schema compatibility with Python ORM
- Identify .NET-specific features (computed columns, spatial types)
- Plan schema modifications if needed
- Consider backward compatibility during transition

**2. ORM Model Creation**

Create Python ORM models:
- Map Entity Framework entities to SQLAlchemy/Django models
- Preserve relationships (one-to-many, many-to-many)
- Implement database constraints and indexes
- Handle custom types and converters

**3. Data Migration Scripts**

If database changes are required:
```bash
python scripts/generate_migration.py --from-dotnet-models /path/to/models
```

Create Alembic (SQLAlchemy) or Django migrations for schema changes.

### Phase 5: Testing and Validation

**1. API Testing**

Implement comprehensive API tests:
- Unit tests for business logic
- Integration tests for endpoints
- Test authentication and authorization flows
- Validate error handling and edge cases

Use pytest for Python backend testing.

**2. Frontend Testing**

Test React components and integration:
- Unit tests with Jest and React Testing Library
- Component integration tests
- End-to-end tests with Cypress or Playwright
- Visual regression testing if needed

**3. Data Integrity Verification**

Ensure data consistency:
- Compare database query results between .NET and Python
- Validate CRUD operations match expected behavior
- Test data migrations if performed
- Verify relationships and cascading deletes

### Phase 6: Deployment Strategy

**1. Environment Configuration**

Set up deployment environments:
- Configure environment variables for both frontend and backend
- Set up secrets management (database credentials, API keys)
- Prepare environment-specific configs (dev, staging, production)

**2. Backend Deployment**

Deploy Python API:
- Choose hosting platform (AWS, Azure, Google Cloud, Heroku, DigitalOcean)
- Set up WSGI/ASGI server (Gunicorn, Uvicorn)
- Configure reverse proxy (Nginx, Apache)
- Implement health checks and monitoring
- Set up database connection pooling

**3. Frontend Deployment**

Deploy React application:
- Build production bundle
- Choose static hosting (Netlify, Vercel, S3 + CloudFront)
- Configure environment-specific API endpoints
- Set up CDN for assets
- Implement cache strategies

**4. Migration Strategy**

Plan the cutover:
- **Big Bang**: Complete switch at once (higher risk, faster completion)
- **Strangler Fig**: Gradually migrate features (lower risk, longer timeline)
- **Parallel Run**: Run both systems temporarily for validation

## Execution Guidelines

### Order of Operations

1. Start with backend API migration for critical business logic
2. Create frontend components as backend endpoints become available
3. Test integration continuously during development
4. Deploy to staging environment for validation
5. Perform final cutover with rollback plan

### Common Pitfalls to Avoid

- **Don't replicate technical debt**: Use migration as opportunity to improve architecture
- **Watch for N+1 queries**: Python ORMs handle lazy loading differently than EF
- **Async patterns**: Be mindful of async/await differences between C# and Python
- **Error handling**: Ensure Python exception handling matches .NET try-catch patterns
- **Timezone handling**: .NET and Python handle timezones differently; standardize on UTC
- **Decimal precision**: Financial calculations require careful type mapping

### Code Quality Standards

- Follow PEP 8 for Python code
- Use ESLint and Prettier for React code
- Implement type hints in Python (using mypy)
- Use TypeScript for React if type safety is important
- Write comprehensive docstrings and comments
- Maintain test coverage above 80%

### Performance Considerations

- Profile database queries during migration
- Implement caching strategies early (Redis, in-memory)
- Optimize API response sizes with proper serialization
- Use React.memo and useMemo for expensive components
- Implement pagination for large datasets
- Consider lazy loading for frontend components

## Reference Files

- **architecture-patterns.md**: Detailed architecture patterns for different .NET app types
- **framework-equivalents.md**: Quick-reference tables mapping .NET technologies to Python equivalents
- **orm-migration.md**: ORM mapping patterns and common translations
- **authentication-patterns.md**: Authentication implementation examples
- **api-integration.md**: API client patterns and best practices
- **testing-strategies.md**: Comprehensive testing approaches for both stacks

## Scripts

- **assess_dotnet_app.py**: Generates migration inventory from .NET project
- **init_python_backend.py**: Scaffolds Python backend project structure
- **generate_migration.py**: Creates database migration from .NET models
- **convert_razor_to_jsx.py**: Assists in converting Razor syntax to JSX

## Assets

- **react-project-template/**: Base React project structure with recommended setup
- **docker-compose.yml**: Full-stack Docker Compose configuration (PostgreSQL, Redis, Backend, Frontend, Nginx)
- **.env.example**: Environment variables template for configuration

## Notes

- This skill assumes familiarity with both .NET and modern Python/React development
- Adjust complexity and depth based on application size and team expertise
- Consider incremental migration for large applications
- Maintain documentation throughout the migration process
- Plan for knowledge transfer if team skills differ between stacks
