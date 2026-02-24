# Stack Comparison Reference

## Frontend Framework Comparison

| Criteria | React + Vite | Next.js | Angular | Vue 3 |
|---|---|---|---|---|
| **Best for** | SPA, no SEO needs, team already knows React | SEO required, SSR/SSG needed | Large enterprise, strong typing culture | Smaller teams, gentle learning curve |
| **Learning curve** | Medium | Medium-High | High | Low-Medium |
| **TypeScript support** | Excellent | Excellent | First-class (built-in) | Excellent |
| **JSP dev familiarity** | Low (but most common) | Low | Low-Medium | Low |
| **Ecosystem maturity** | Very high | High | Very high | High |
| **Deployment complexity** | Simple (static files) | Requires Node server | Simple (static files) | Simple (static files) |
| **Recommended for JSP migration** | ✅ Default choice | ✅ If SEO matters | ⚠️ Only if team prefers it | ⚠️ Smaller teams only |

**Recommendation**: Default to **React + Vite + TypeScript**. Use **Next.js** if SEO is a requirement. The React ecosystem has the widest talent pool and the most mature component library options.

---

## React Component Library Comparison

| Library | Style Approach | Customization | Accessibility | Best For |
|---|---|---|---|---|
| **Material UI (MUI)** | CSS-in-JS, Material Design | High | Strong | Enterprise, large teams |
| **Ant Design** | CSS Modules | High | Good | Data-heavy enterprise apps |
| **Shadcn/ui** | Tailwind CSS, copy-paste | Very High | Strong | Teams who want full control |
| **Chakra UI** | CSS-in-JS | High | Excellent | Rapid development |
| **Tailwind CSS (only)** | Utility classes | Maximum | Depends on usage | Teams with strong CSS skills |

**Recommendation**: **MUI** for enterprise Java migrations (familiar "form-heavy" paradigm). **Shadcn/ui + Tailwind** for greenfield-feeling migrations with design system budget.

---

## Backend Framework Comparison

| Criteria | Spring Boot | Quarkus | Micronaut | Jakarta EE (raw) |
|---|---|---|---|---|
| **Migration effort from Spring MVC** | Very low | Medium | Medium | Low |
| **Startup time** | Moderate | Very fast | Fast | Moderate |
| **Memory footprint** | Higher | Very low | Low | Moderate |
| **Native image (GraalVM)** | Supported | First-class | First-class | Limited |
| **Ecosystem** | Massive | Growing | Moderate | Large |
| **Container/K8s fit** | Good (with tuning) | Excellent | Excellent | Good |
| **Team ramp-up from Spring MVC** | None (same ecosystem) | 1–2 weeks | 1–2 weeks | Minimal |
| **Recommended for JSP migration** | ✅ Default choice | ⚠️ If K8s optimization is priority | ⚠️ Advanced teams only | ❌ No advantage |

**Recommendation**: **Spring Boot 3.x** is the default for Java JSP migrations. Same ecosystem, massive documentation, lowest transition risk.

---

## State Management Comparison (React)

| Library | Complexity | Best For | Learning Curve |
|---|---|---|---|
| **React Query (TanStack Query)** | Low | Server state, API data, caching | Low |
| **Zustand** | Very Low | Client-only state | Very Low |
| **Redux Toolkit** | Medium | Complex global state, large teams | Medium |
| **Jotai** | Very Low | Atomic state, fine-grained reactivity | Low |
| **Context API** | Very Low | Simple shared state only | Very Low |

**Recommendation**: **React Query + Zustand** covers 90% of JSP migration scenarios. React Query handles all API/server state (replacing JSP form submissions). Zustand handles UI-only global state (modals, filters, etc.).

---

## Authentication Strategy Comparison

| Current JSP Auth | Recommended Migration Path | Notes |
|---|---|---|
| Tomcat JAAS / Container-managed | Spring Security + JWT | Most common; extract to Spring Security first |
| Spring Security (form login) | Spring Security + JWT or OAuth2 | Relatively straightforward |
| Custom session-based auth | Spring Security + JWT | Audit thoroughly first |
| LDAP / Active Directory | Spring Security LDAP + JWT | Keep LDAP integration, wrap with JWT |
| SAML SSO | Spring Security SAML + JWT | Complex; spike early |
| OAuth2 / OIDC (existing) | Passthrough to frontend | Easiest path |

**Key principle**: The React frontend should be stateless. All auth state lives in JWT (access + refresh tokens). Never pass session cookies to the React app.

---

## Form Handling Migration Map

| JSP Pattern | React Equivalent |
|---|---|
| `<form action="..." method="POST">` | `<form onSubmit={handleSubmit}>` via React Hook Form |
| JSTL `<c:if>` validation display | Zod schema + React Hook Form errors |
| Spring `<form:form>` binding | Controlled inputs bound to React Hook Form |
| `BindingResult` server validation | API returns 400 + validation errors; display with React Hook Form `setError` |
| File upload `<input type="file">` | React file input + multipart POST to Spring Boot endpoint |
| Custom tag for date picker | React date picker component (e.g., React DatePicker) |

---

## Infrastructure & Deployment Comparison

| Option | Complexity | Best For |
|---|---|---|
| **AKS (Azure Kubernetes Service)** | High | Enterprise, multi-app, existing K8s investment |
| **Azure App Service** | Low | Smaller apps, simpler ops |
| **Azure Static Web Apps + App Service** | Low-Medium | React SPA + Spring Boot API |
| **Azure Container Apps** | Medium | Serverless containers, scale-to-zero |
| **AWS ECS / Fargate** | Medium | AWS-first organizations |
| **On-prem with Docker Compose** | Low | Dev/test; not recommended for prod |

**For AKS deployments**: Ensure the Spring Boot app is containerized (Docker + distroless or Eclipse Temurin base), and expose React as a static asset via nginx sidecar or Azure CDN.