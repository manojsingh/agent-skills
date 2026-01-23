# CI/CD Pipeline Templates

This directory contains CI/CD pipeline templates for different platforms.

## Available Templates

### 1. GitHub Actions (`github-actions.yml`)

**Features:**
- Backend testing (Python, pytest)
- Frontend testing (Node.js, Jest)
- Code coverage reporting (Codecov)
- Security scanning (Snyk, Trivy)
- Docker image building
- Automated deployment to staging/production
- E2E tests with Playwright
- Slack notifications

**Setup:**

1. Copy to `.github/workflows/ci-cd.yml`:
   ```bash
   mkdir -p .github/workflows
   cp assets/cicd-templates/github-actions.yml .github/workflows/ci-cd.yml
   ```

2. Configure secrets in GitHub repository settings:
   - `SNYK_TOKEN` - Snyk API token
   - `STAGING_HOST` - Staging server hostname
   - `STAGING_USER` - SSH username
   - `STAGING_SSH_KEY` - SSH private key
   - `PRODUCTION_HOST` - Production server hostname
   - `PRODUCTION_USER` - SSH username
   - `PRODUCTION_SSH_KEY` - SSH private key
   - `SLACK_WEBHOOK` - Slack webhook URL

3. Customize:
   - Update `PYTHON_VERSION` and `NODE_VERSION`
   - Update deployment URLs
   - Modify test commands if needed
   - Adjust deployment steps for your infrastructure

---

### 2. GitLab CI/CD (`gitlab-ci.yml`)

**Features:**
- Backend and frontend testing
- Code coverage visualization
- Security scanning (Safety, Bandit)
- Docker image building
- Automated deployment with manual approval for production
- E2E testing on staging

**Setup:**

1. Copy to `.gitlab-ci.yml`:
   ```bash
   cp assets/cicd-templates/gitlab-ci.yml .gitlab-ci.yml
   ```

2. Configure CI/CD variables in GitLab:
   - `STAGING_HOST` - Staging server hostname
   - `STAGING_USER` - SSH username
   - `STAGING_SSH_KEY` - SSH private key
   - `PRODUCTION_HOST` - Production server hostname
   - `PRODUCTION_USER` - SSH username
   - `PRODUCTION_SSH_KEY` - SSH private key

3. Enable GitLab Container Registry

4. Customize stages and jobs as needed

---

## Common Configuration

### Backend Testing Requirements

Create `backend/requirements-dev.txt`:
```
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0
flake8>=6.0.0
mypy>=1.4.0
black>=23.0.0
isort>=5.12.0
```

### Frontend Testing Setup

Ensure `frontend/package.json` has:
```json
{
  "scripts": {
    "test": "jest",
    "lint": "eslint src --ext .js,.jsx,.ts,.tsx",
    "type-check": "tsc --noEmit"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "eslint": "^8.0.0",
    "typescript": "^5.0.0"
  }
}
```

---

## Pipeline Stages

### 1. Test Stage

**Backend Tests:**
- Linting with flake8
- Type checking with mypy
- Unit/integration tests with pytest
- Code coverage reporting

**Frontend Tests:**
- Linting with ESLint
- Type checking with TypeScript
- Unit tests with Jest
- Component tests with React Testing Library

**Security Scanning:**
- Dependency vulnerability scanning
- SAST (Static Application Security Testing)
- Container image scanning

### 2. Build Stage

**Docker Images:**
- Multi-stage builds for optimization
- Layer caching for faster builds
- Tagged with commit SHA and branch name
- Pushed to container registry

### 3. Deploy Stage

**Staging:**
- Automated deployment on `develop` branch
- Database migrations applied
- Services restarted

**Production:**
- Manual approval (GitLab) or automated (GitHub)
- Deployed from `main` branch
- Includes smoke tests
- Rollback capability

---

## Best Practices

### 1. Environment Separation

Use different environments for each stage:
```yaml
environment:
  name: staging
  url: https://staging.yourdomain.com
```

### 2. Secrets Management

Never hardcode secrets:
- Use CI/CD variables/secrets
- Rotate credentials regularly
- Use least privilege access

### 3. Caching

Speed up pipelines with caching:
```yaml
# GitHub Actions
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

# GitLab CI
cache:
  paths:
    - .pip
    - node_modules/
```

### 4. Parallel Jobs

Run independent jobs in parallel:
```yaml
jobs:
  backend-tests:
    # ...
  frontend-tests:
    # ...
  # Both run simultaneously
```

### 5. Fail Fast

Stop pipeline early on critical failures:
```yaml
- name: Critical test
  run: pytest critical_tests/
  # If this fails, pipeline stops
```

### 6. Artifacts

Preserve test results and reports:
```yaml
artifacts:
  paths:
    - coverage/
    - test-results/
  expire_in: 30 days
```

---

## Advanced Configurations

### Blue-Green Deployment

```yaml
deploy:production:
  script:
    - docker-compose -f docker-compose.green.yml up -d
    - # Run health checks
    - # Switch traffic from blue to green
    - docker-compose -f docker-compose.blue.yml down
```

### Canary Deployment

```yaml
deploy:canary:
  script:
    - # Deploy to 10% of servers
    - # Monitor metrics
    - # Gradually increase to 100%
```

### Database Migrations with Rollback

```yaml
- name: Backup database
  run: |
    docker-compose exec postgres pg_dump > backup.sql
- name: Apply migrations
  run: |
    docker-compose exec backend alembic upgrade head
  on_failure:
    - docker-compose exec postgres psql < backup.sql
```

---

## Monitoring

### Add Health Checks

```yaml
- name: Health check
  run: |
    for i in {1..10}; do
      if curl -f $DEPLOY_URL/api/health; then
        exit 0
      fi
      sleep 10
    done
    exit 1
```

### Performance Testing

```yaml
performance:test:
  script:
    - artillery run performance-tests.yml
    - # Fail if response time > threshold
```

---

## Troubleshooting

### Pipeline Fails

1. Check logs in CI/CD interface
2. Run tests locally with same environment
3. Verify secrets/variables are set
4. Check service dependencies (DB, Redis)

### Slow Pipelines

1. Use caching effectively
2. Parallelize independent jobs
3. Optimize Docker builds (multi-stage)
4. Use smaller base images

### Deployment Failures

1. Check server connectivity
2. Verify SSH keys are correct
3. Check disk space on server
4. Review deployment logs
5. Test deployment script locally

---

## Integration with Monitoring

### Sentry Error Tracking

```yaml
- name: Set Sentry release
  run: |
    curl -sL https://sentry.io/get-cli/ | bash
    sentry-cli releases new "$CI_COMMIT_SHORT_SHA"
    sentry-cli releases set-commits "$CI_COMMIT_SHORT_SHA" --auto
```

### Datadog Metrics

```yaml
- name: Send deployment metric
  run: |
    curl -X POST "https://api.datadoghq.com/api/v1/events" \
      -H "DD-API-KEY: $DD_API_KEY" \
      -d @- << EOF
    {
      "title": "Deployment",
      "text": "Deployed $CI_COMMIT_SHORT_SHA to production",
      "tags": ["environment:production"]
    }
    EOF
```

---

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [12-Factor App Methodology](https://12factor.net/)
