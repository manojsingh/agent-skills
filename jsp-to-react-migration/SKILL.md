---
name: jsp-to-react-migration
description: "Deep assessment and detailed migration report for modernizing Java JSP/Tag Library applications on Tomcat to a React frontend + Java backend (Spring Boot REST/GraphQL) architecture. Use this skill whenever a user wants to assess a JSP application for modernization, plan a migration from server-side Java rendering to a React/SPA frontend, evaluate the effort involved in a JSP-to-React refactor, generate a migration strategy or report, or understand the risks and phases of moving from JSP/Tomcat to a decoupled frontend/backend stack. Also trigger for phrases like 'modernize my Java app', 'move from JSP to React', 'assess my legacy Java frontend', 'JSP migration plan', or 'how hard is it to convert our JSP app'."
---

# JSP-to-React Migration Assessment Skill

This skill guides Claude through conducting a thorough technical assessment of a Java JSP/Tag Library application and producing a professional, detailed migration report covering architecture, effort estimation, risk analysis, and a phased migration roadmap.

---

## Workflow Overview

1. **Gather application intelligence** — collect as much detail about the app as possible
2. **Perform structured analysis** — assess each dimension using the scoring framework
3. **Generate the report** — produce a comprehensive Word document (.docx) using the docx skill

> **Important**: Before generating the report, always read `/mnt/skills/public/docx/SKILL.md` to produce a properly formatted Word document.

---

## Phase 1: Information Gathering

Ask the user (or extract from any uploaded files/code) for the following. Not all are required — work with what's available and flag gaps in the report.

### Application Basics
- Application name and business domain
- Estimated number of JSP pages / screens
- Approximate codebase size (LOC or file count)
- Age of the application and last major update
- Team size and Java/frontend experience level

### Frontend Layer (JSP)
- Tag libraries in use (JSTL, Struts, Spring MVC tags, custom tags?)
- Use of scriptlets (Java code embedded in JSPs) — heavy, moderate, or none?
- JavaScript usage (jQuery, vanilla JS, or modern frameworks already partially adopted?)
- CSS framework (Bootstrap, custom, none?)
- Number of reusable tag components / includes
- Any existing partial React or SPA screens?

### Backend Layer
- Framework: Spring MVC, Struts, raw Servlets, or other?
- Authentication: Container-managed (Tomcat JAAS), Spring Security, custom?
- Session management: heavy session state, or mostly stateless?
- ORM/database: Hibernate, JPA, JDBC, MyBatis?
- Existing REST APIs? (yes/no — crucial for migration strategy)
- Microservices or monolith?

### Business Logic Distribution
- Is business logic in JSPs (scriptlets/tag libs) or properly in service/controller layers?
- Are there complex workflows driven by JSP form submissions?
- Any file upload, PDF generation, report generation features?

### Non-Functional Concerns
- SEO requirements? (affects React vs Next.js choice)
- Real-time features? (WebSockets, server-sent events?)
- Performance SLAs?
- Multi-tenancy or internationalization?
- Accessibility requirements (WCAG level)?

### Operational Context
- Current deployment: on-prem Tomcat, cloud VM, or container?
- Target deployment: Kubernetes/AKS, Azure App Service, AWS, other?
- CI/CD pipeline in place?
- Test coverage: unit tests, integration tests?

---

## Phase 2: Scoring & Analysis Framework

Score each dimension 1–5 (1 = simple/low-risk, 5 = complex/high-risk). Use these to estimate effort and highlight risk areas.

### Complexity Dimensions

| Dimension | Score (1–5) | Notes |
|---|---|---|
| JSP scriptlet density | | 1=none, 5=heavy embedded logic |
| Custom tag library complexity | | 1=JSTL only, 5=many complex custom tags |
| Business logic in view layer | | 1=clean MVC, 5=logic mixed into JSPs |
| Session state complexity | | 1=stateless, 5=heavy session-driven flows |
| Authentication complexity | | 1=simple, 5=container-managed or complex SSO |
| Existing REST API surface | | 1=full REST, 5=no APIs exist |
| JavaScript/UI complexity | | 1=minimal JS, 5=complex jQuery spaghetti |
| Test coverage | | 1=well tested, 5=no tests |
| Team frontend readiness | | 1=React experts, 5=no frontend experience |
| Page/screen count | | 1=<10 pages, 5=>100 pages |

**Total complexity score** (out of 50): Sum all scores.

### Effort Estimate Tiers
- **10–20**: Low effort (3–6 months for small team)
- **21–33**: Medium effort (6–12 months)
- **34–42**: High effort (12–18 months)
- **43–50**: Very high effort (18+ months, consider phased strangler fig over 2+ years)

---

## Phase 3: Migration Strategy Recommendation

Based on the complexity score and app characteristics, recommend one of:

### Strategy A: Big Bang Rewrite
- **When**: Score ≤ 20, app < 20 screens, team has React expertise, business can tolerate cutover risk
- **Approach**: Parallel development of full React + Spring Boot app; feature-freeze old app; hard cutover
- **Timeline**: Typically 3–6 months

### Strategy B: Strangler Fig (Recommended for most)
- **When**: Score 21–42, moderate complexity
- **Approach**: Reverse proxy (nginx/API Gateway) routes traffic; new React screens replace JSP screens page-by-page; old and new coexist; JSPs decommissioned incrementally
- **Timeline**: 6–18 months depending on scope

### Strategy C: Micro-frontend Bridge
- **When**: Score ≥ 35, large app, business continuity is critical, team is split
- **Approach**: Embed React components inside JSP pages using Web Components or iframes; extract backend APIs incrementally; full SPA comes later
- **Timeline**: 18–30+ months

### Strategy D: Backend-First
- **When**: No existing REST APIs, high session/auth complexity
- **Approach**: Build Spring Boot REST API layer first while keeping JSP frontend; validate APIs; then migrate frontend
- **Timeline**: Add 3–6 months to any of the above

---

## Phase 4: Phased Roadmap

Generate a phase-by-phase plan tailored to the chosen strategy. Use this template:

### Phase 0: Foundation (Weeks 1–4)
- Architecture decision records (ADR) for stack choices
- Development environment setup (DevContainers, monorepo structure)
- CI/CD pipeline foundation
- API design standards and authentication strategy

### Phase 1: Backend Extraction (Weeks 4–12)
- Extract business logic from JSPs into service layer (if not already done)
- Build Spring Boot REST API layer
- Implement Spring Security with JWT or OAuth2
- API documentation (OpenAPI/Swagger)
- Unit/integration test baseline

### Phase 2: Frontend Foundation (Weeks 8–16, overlaps Phase 1)
- React project setup (Vite or Next.js), TypeScript, component library
- Design system / shared component library
- Auth integration (JWT handling, route guards)
- State management setup (React Query + Zustand/Redux Toolkit)
- Storybook for component development

### Phase 3: Screen Migration (Weeks 12–N)
- Priority order: high-traffic / high-business-value screens first
- For each JSP → React screen:
  - Map tag lib components to React components
  - Wire to REST API endpoints
  - Replicate form validation (React Hook Form + Zod)
  - E2E test with Playwright/Cypress
  - Canary deploy via reverse proxy

### Phase 4: Decommission & Cutover
- Retire remaining JSPs
- Remove Tomcat JSP dependencies
- Performance baseline and load testing
- Monitoring and alerting (Prometheus, Grafana, Application Insights)

---

## Phase 5: Risk Register

Always include a risk register in the report. Use this as a starting template and add app-specific risks:

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Business logic hidden in JSPs | High | High | Audit and extract before frontend migration |
| Session state migration complexity | Medium | High | Stateless API design from day one |
| Team React skill gap | Variable | High | Training + pairing + hiring plan |
| SEO regression (SPA vs SSR) | Low–Med | High | Use Next.js if SEO is critical |
| Auth/SSO integration complexity | Medium | High | Spike auth early in Phase 1 |
| No existing test coverage | High | High | Write API contract tests before migration |
| Scope creep / feature parity paralysis | High | Medium | Strict feature freeze on old app during migration |
| Custom tag lib behaviour differences | Medium | Medium | Document and test all tag lib behaviours before decommission |

---

## Report Structure

Generate a Word document (.docx) with the following structure. **Always consult the docx skill before generating**.

```
1. Executive Summary
   - App overview
   - Recommended strategy (1 paragraph)
   - Headline effort estimate
   - Top 3 risks

2. Application Assessment
   - Current Architecture Overview
   - Technology Inventory (table)
   - Complexity Scorecard (table)
   - Key Findings (narrative)

3. Target Architecture
   - Architecture diagram description
   - Frontend stack recommendation with rationale
   - Backend stack recommendation with rationale
   - Infrastructure / deployment target

4. Migration Strategy
   - Chosen strategy with rationale
   - Why alternatives were not chosen

5. Phased Roadmap
   - Phase-by-phase breakdown (table + narrative)
   - Milestone timeline (Gantt-style table)
   - Team composition recommendation

6. Effort Estimate
   - Summary table by phase
   - Assumptions and exclusions

7. Risk Register
   - Full risk table with mitigations

8. Recommendations & Next Steps
   - Immediate actions (next 30 days)
   - Quick wins
   - Key decisions needed from stakeholders

9. Appendix
   - Technology comparison tables (React vs Angular vs Vue, Spring Boot vs Quarkus, etc.)
   - Sample DevContainer configuration
   - Sample monorepo structure
```

---

## Tips for a High-Quality Report

- **Be specific**: If the user gives you page counts, team sizes, or framework names — use them. Avoid vague estimates.
- **Tailor the strategy**: Don't recommend "Big Bang" for a 150-page enterprise app. Match the strategy to the evidence.
- **Flag information gaps**: If the user hasn't provided information about auth or session state, note it as a "discovery item" in the report rather than assuming.
- **Include a quick wins section**: Always identify 2–3 things the team can do in the first 30 days to build confidence and reduce risk.
- **Use tables liberally**: Complexity scorecards, risk registers, and roadmap tables are much more readable than prose.
- **Executive summary first**: The exec summary must stand alone — a non-technical stakeholder should be able to read just that section and understand the situation.

---

## Reference Files

- `references/stack-comparison.md` — Detailed technology comparison tables for frontend and backend choices
- `references/sample-monorepo-structure.md` — Example monorepo layout for React + Spring Boot projects
- `references/interview-questions-extended.md` — Extended interview guide for complex enterprise scenarios