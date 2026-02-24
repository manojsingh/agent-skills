# Extended Interview Guide: Enterprise JSP Migration Scenarios

Use these questions when the initial assessment reveals complexity that warrants deeper discovery.
Not all sections apply to every engagement — pick the relevant ones.

---

## Section 1: Page & Component Inventory

- Can you provide a list of all JSP pages? (or let Claude examine the codebase)
- Which pages have the most user traffic? (helps prioritize migration order)
- How many distinct "screens" exist vs how many JSP files? (many-to-one is common with includes)
- Are there any JSP pages that are purely layout/include fragments (headers, footers, nav)?
- Which JSP pages handle the most complex business workflows? (multi-step forms, wizards?)
- Are there any pages with real-time requirements? (polling, live updates, auto-refresh?)

## Section 2: Custom Tag Library Deep Dive

- Do you have custom TLDs (`.tld` files)? How many?
- Do any tag libs call external services or databases directly?
- Are tag libs shared across multiple applications?
- Are there tag libs that handle pagination, sorting, or grid rendering?
- Any tags that generate complex HTML structures (trees, nested tabs, accordions)?

## Section 3: Authentication & Security

- What is the exact current auth mechanism? (form login, Basic Auth, SAML, OIDC, custom?)
- Is there Single Sign-On (SSO) across multiple apps?
- Are there different user roles? How complex is the authorization model?
- Does the app use Tomcat realms? If so, which type (JDBC, LDAP, memory)?
- Are there CSRF protections in place today? (Spring Security or custom?)
- Any OAuth2 integration with third-party providers (Google, Azure AD, Okta)?
- Any secrets stored in web.xml or application context? (need to migrate to vault)

## Section 4: Data & Backend

- What database(s) are used? (PostgreSQL, Oracle, SQL Server, MySQL?)
- Any stored procedures or database-side business logic?
- Any NoSQL/cache stores? (Redis, MongoDB, Memcached?)
- Are there batch jobs or scheduled tasks? (Quartz, Spring Batch?)
- Any message queues? (JMS, ActiveMQ, Kafka, Azure Service Bus?)
- Any integration with external SOAP/REST services?
- Any file system dependencies? (reading/writing files on disk — tricky in K8s)
- Are database connections managed by Tomcat JNDI? (needs migration to Spring Boot datasource)

## Section 5: Testing & Quality

- What percentage of business logic has unit tests?
- Are there integration or end-to-end tests? If so, what framework?
- Is there automated UI testing? (Selenium, etc.)
- What does the CI/CD pipeline look like today?
- Is there a staging/UAT environment that mirrors production?

## Section 6: Operational & Compliance

- Are there any regulatory compliance requirements? (HIPAA, PCI-DSS, SOC 2, GDPR?)
- Any audit logging requirements that touch the UI layer?
- Are there SLAs for availability or performance that the migration must maintain?
- Any geographic restrictions on where data can be stored or processed?
- Is there a change control board or release freeze periods to be aware of?

## Section 7: Team & Organizational

- Who are the key stakeholders? (Product, Engineering, Operations, Security?)
- Is there a dedicated migration team or will it be current team + new work?
- What is the team's current React/TypeScript experience level?
- Is there budget for external consultants or training?
- Is there appetite for a phased approach or pressure for a hard cutover?
- Are there parallel feature development requirements that can't pause?

---

## Red Flags to Watch For

These indicate significantly higher complexity — flag in the report:

- **JSP scriptlets with 50+ lines of Java code** — significant refactoring required
- **Custom tag libs that call the database directly** — architectural anti-pattern needing redesign
- **Tomcat JNDI datasource + JAAS auth** — both need migration, easy to miss
- **Struts 1.x or older MVC** — pre-Spring, very different paradigm
- **JSP-to-JSP form submissions driving complex state machines** — hardest pattern to migrate
- **iFrames or JSP page composition patterns** — unusual layouts that don't map cleanly to React
- **Shared JSP tag libs used by multiple applications** — need a shared React component library strategy
- **No existing automated tests** — migration risk is very high without test safety net
- **Single developer who knows the whole codebase** — bus factor risk; needs knowledge transfer first
- **More than 200 JSP pages** — almost certainly requires Strangler Fig, not Big Bang

---

## Useful Codebase Analysis Commands

If Claude has access to the codebase, run these to quickly gather stats:

```bash
# Count JSP files
find . -name "*.jsp" | wc -l

# Count scriptlet usage (embedded Java in JSPs)
grep -rl "<%" --include="*.jsp" . | wc -l

# List all tag library imports
grep -rh "<%@ taglib" --include="*.jsp" . | sort | uniq -c | sort -rn

# Count Java files
find . -name "*.java" | wc -l

# Find all TLD files (custom tag libs)
find . -name "*.tld"

# Find all Servlet mappings
grep -r "url-pattern" --include="web.xml" .

# Check for Spring MVC controllers
grep -rl "@Controller\|@RestController" --include="*.java" . | wc -l

# Check for existing REST endpoints
grep -rl "@RequestMapping\|@GetMapping\|@PostMapping" --include="*.java" . | wc -l

# Find session usage
grep -rn "HttpSession\|session.setAttribute\|session.getAttribute" --include="*.java" . | wc -l
```