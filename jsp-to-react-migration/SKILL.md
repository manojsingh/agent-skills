---
name: jsp-to-react-migration
description: "Assess a Java JSP/TagLib app on Tomcat and produce a migration plan to React + Spring Boot APIs. Emphasize evidence-based scoring, strategy selection, roadmap, effort, and risks."
---

# JSP-to-React Migration Assessment Skill (Token-Optimized)

## Output Contract
- Produce a **migration assessment report** (preferred: .docx via docx skill when available).
- Be **evidence-based**. If data is missing, record as **Discovery Needed** (do not assume).
- **Only include sections that apply** (or mark explicitly N/A). Avoid long explanations.

> If generating .docx: read `/mnt/skills/public/docx/SKILL.md` first.

---

## Phase 0 — Inputs (Ask/Extract)
Collect what you can; ask only for missing critical items:

### A) Scope
- App/domain name
- # JSP files, # screens (if different), high-traffic pages
- Age + last major update
- Team size + React/TS experience

### B) Frontend (JSP)
- Tag libs: JSTL / Spring / Struts / custom TLD count
- Scriptlets density: none / light / moderate / heavy
- Includes/fragments patterns
- JS: none / jQuery / mixed / modern
- CSS: Bootstrap / custom / none
- Any existing React/SPA parts?

### C) Backend
- Framework: Spring MVC / Struts / Servlets / other
- Auth: container-managed / Spring Security / SSO (SAML/OIDC) / custom
- Session dependence: low/med/high
- Data: DB type, ORM (JPA/Hibernate/JDBC/MyBatis), queues, batch jobs
- Existing REST APIs? (% coverage, quality)

### D) Ops/Delivery
- Deploy: on-prem VM / cloud VM / containers / K8s
- CI/CD: none/basic/mature
- Testing: unit/integration/e2e coverage level
- Compliance/security constraints

**Minimum required to score + recommend strategy**: A + scriptlets + taglibs + auth/session + REST surface + test coverage + page/screen count.

---

## Phase 1 — Rapid Codebase Signals (If repo access)
Prefer short quantitative signals:
- JSP count, scriptlet count, taglib imports, TLD count
- Session usage hotspots
- Controller/API annotation counts

(Include commands as an appendix only if requested.)

---

## Phase 2 — Complexity Scorecard (1–5 each)
Score, add 1-line justification per row.

| Dimension | Score | Evidence |
|---|---:|---|
| Scriptlets | | |
| Custom tag libs | | |
| View-layer business logic | | |
| Session complexity | | |
| Auth/SSO complexity | | |
| REST API readiness | | |
| UI JS complexity | | |
| Test coverage | | |
| Team React readiness | | |
| Page/screen count | | |

**Total (0–50)** = sum.

### Effort Tier (guideline)
- 10–20: Low (3–6 months)
- 21–33: Medium (6–12 months)
- 34–42: High (12–18 months)
- 43–50: Very high (18+ months)

---

## Phase 3 — Pick Strategy (choose ONE; name alternatives briefly)
### A) Big Bang
Use when: low complexity + small scope + strong team + cutover acceptable.

### B) Strangler Fig (default)
Use when: medium/high scope; coexistence required; incremental screen replacement.

### C) Micro-frontend Bridge
Use when: very large app, continuity critical, need embed React in JSP.

### D) Backend-first (modifier)
Use when: no REST APIs + complex auth/session → build APIs before UI migration.

---

## Phase 4 — Roadmap (phases + milestones)
Keep each phase to: goals, key deliverables, exit criteria.

- Phase 0 Foundation (env, CI, standards, ADRs)
- Phase 1 Backend/API (auth, API layer, OpenAPI, tests baseline)
- Phase 2 Frontend foundation (React/Vite+TS, routing, component library, state)
- Phase 3 Screen migration (ordered backlog + acceptance tests)
- Phase 4 Decommission/cutover (perf, monitoring, remove JSP/Tomcat deps)

Include a simple milestone table:
- Milestone | Duration | Dependencies | Output

---

## Phase 5 — Risks (Top 8–12 max)
Risk register table:

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|

Prefer risks tied to evidence (e.g., “scriptlets in checkout.jsp”).

---

## Recommendations (Next 30 Days)
List 5–10 concrete actions:
- discovery items
- spikes (auth, routing/proxy, API contract)
- test harness/CI
- first screen selection + definition of done

---

## Reference Usage Policy (token control)
- Do **not** paste large comparison tables unless asked.
- If needed, summarize choices in **3–6 bullets** and link to appendix.
- Prefer **defaults** unless constraints contradict:
  - Frontend: React + Vite + TypeScript
  - Server state: React Query
  - Client state: Zustand
  - Backend: Spring Boot 3 + Spring Security
  - Migration approach: Strangler Fig unless clearly Big Bang

## Appendix (optional)
Include only if requested:
- stack comparison tables
- sample monorepo structure
- extended interview question bank