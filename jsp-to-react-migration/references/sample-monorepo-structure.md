# Sample Monorepo Structure: React + Spring Boot

This is a recommended monorepo layout for a JSP-to-React migration project.
Use this as a starting point in the report appendix.

```
my-app/
├── .devcontainer/                    # DevContainer config for consistent dev environments
│   ├── devcontainer.json
│   └── docker-compose.yml
│
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Build + test on PR
│       ├── deploy-staging.yml        # Deploy to staging on merge to main
│       └── deploy-prod.yml           # Deploy to prod on release tag
│
├── frontend/                         # React application
│   ├── public/
│   ├── src/
│   │   ├── api/                      # API client functions (React Query hooks)
│   │   │   ├── auth.ts
│   │   │   ├── users.ts
│   │   │   └── index.ts
│   │   ├── components/               # Shared UI components
│   │   │   ├── ui/                   # Atomic design: atoms
│   │   │   ├── forms/                # Form components
│   │   │   └── layout/               # Layout components (Shell, Sidebar, etc.)
│   │   ├── features/                 # Feature-based modules (mirrors app domains)
│   │   │   ├── auth/
│   │   │   │   ├── LoginPage.tsx
│   │   │   │   ├── useAuth.ts
│   │   │   │   └── authStore.ts
│   │   │   ├── dashboard/
│   │   │   └── users/
│   │   ├── hooks/                    # Shared custom hooks
│   │   ├── stores/                   # Zustand stores (client-side state)
│   │   ├── types/                    # TypeScript type definitions
│   │   ├── utils/                    # Utility functions
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── router.tsx                # React Router v6 routes
│   ├── .env.development
│   ├── .env.production
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   └── Dockerfile                    # Multi-stage: build React + serve with nginx
│
├── backend/                          # Spring Boot application
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/myapp/
│   │   │   │   ├── config/           # Spring configuration classes
│   │   │   │   │   ├── SecurityConfig.java
│   │   │   │   │   ├── CorsConfig.java
│   │   │   │   │   └── OpenApiConfig.java
│   │   │   │   ├── domain/           # Domain model (entities, value objects)
│   │   │   │   │   ├── user/
│   │   │   │   │   └── order/
│   │   │   │   ├── api/              # REST controllers
│   │   │   │   │   ├── AuthController.java
│   │   │   │   │   ├── UserController.java
│   │   │   │   │   └── dto/          # Request/response DTOs
│   │   │   │   ├── service/          # Business logic services
│   │   │   │   ├── repository/       # Spring Data JPA repositories
│   │   │   │   ├── security/         # JWT filter, auth provider
│   │   │   │   └── exception/        # Global exception handler
│   │   │   └── resources/
│   │   │       ├── application.yml
│   │   │       ├── application-dev.yml
│   │   │       └── application-prod.yml
│   │   └── test/
│   │       └── java/com/myapp/
│   │           ├── api/              # Integration tests (MockMvc or RestAssured)
│   │           └── service/          # Unit tests
│   ├── pom.xml (or build.gradle)
│   └── Dockerfile                    # Multi-stage: Maven build + JRE runtime
│
├── infrastructure/                   # Infrastructure as Code
│   ├── terraform/                    # or Bicep/Pulumi
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── modules/
│   │       ├── aks/
│   │       ├── acr/
│   │       └── keyvault/
│   └── k8s/                          # Kubernetes manifests
│       ├── base/
│       │   ├── frontend-deployment.yaml
│       │   ├── backend-deployment.yaml
│       │   ├── ingress.yaml
│       │   └── configmap.yaml
│       └── overlays/
│           ├── staging/
│           └── production/
│
├── docs/
│   ├── architecture/
│   │   ├── decisions/                # ADRs (Architecture Decision Records)
│   │   └── diagrams/
│   ├── api/                          # OpenAPI specs (auto-generated from Spring Boot)
│   └── runbooks/
│
├── scripts/
│   ├── dev-setup.sh                  # One-command local dev setup
│   ├── db-migrate.sh
│   └── smoke-test.sh
│
├── .gitignore
├── docker-compose.yml                # Local development: all services
└── README.md
```

## Key DevContainer Configuration

```json
// .devcontainer/devcontainer.json
{
  "name": "My App Dev",
  "dockerComposeFile": "docker-compose.yml",
  "service": "devcontainer",
  "workspaceFolder": "/workspace",
  "features": {
    "ghcr.io/devcontainers/features/java:1": { "version": "21" },
    "ghcr.io/devcontainers/features/node:1": { "version": "20" },
    "ghcr.io/devcontainers/features/azure-cli:1": {},
    "ghcr.io/devcontainers/features/kubectl-helm-minikube:1": {}
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "vmware.vscode-spring-boot",
        "vscjava.vscode-java-pack",
        "esbenp.prettier-vscode",
        "bradlc.vscode-tailwindcss",
        "ms-azuretools.vscode-docker"
      ]
    }
  },
  "postCreateCommand": "cd frontend && npm install && cd ../backend && mvn install -DskipTests"
}
```

## Local Docker Compose for Development

```yaml
# docker-compose.yml (local dev)
version: '3.8'
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev
    ports: ["5432:5432"]
    volumes: ["postgres_data:/var/lib/postgresql/data"]

  backend:
    build: ./backend
    ports: ["8080:8080"]
    environment:
      SPRING_PROFILES_ACTIVE: dev
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/myapp
    depends_on: [postgres]

  frontend:
    build:
      context: ./frontend
      target: dev
    ports: ["3000:3000"]
    volumes: ["./frontend/src:/app/src"]
    environment:
      VITE_API_BASE_URL: http://localhost:8080

volumes:
  postgres_data:
```