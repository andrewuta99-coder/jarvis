---
name: jarvis-study
version: 0.0.1
description: |
  Subsystem-scoped briefing. Given a topic ("membership management", "leads
  engine", "virtual staging"), produce a thorough, structured brief on that
  subsystem so a fresh agent (or future-you) is ready to add features there
  without re-discovering everything. Caches results in
  .jarvis/subsystems/<slug>.md and auto-refreshes on drift.
  Use when asked to: "study the X workflow", "look into infra for Y",
  "get me up to speed on Z", "prime me for adding a feature to W". (jarvis)
allowed-tools: [Bash, Read, Write, Edit, Agent]
triggers:
  - jarvis study
  - study the infra for
  - look into the infra
  - get me ready to add to
  - prime me for
  - subsystem brief
---

# /jarvis-study — subsystem-scoped briefing

You normally prompt "study the X workflow ready for me to add a new feature" before any focused work. This skill codifies that recipe so every study is consistent, thorough, and cached.

It differs from siblings:
- `/jarvis-doctor` answers "what's wrong?" (health)
- `/jarvis-adopt` is one-time onboarding
- **`/jarvis-study` answers "what is?" — scoped to one subsystem, ready-for-work.**

The deliverable is a brief in `.jarvis/subsystems/<slug>.md` and a compact summary printed back to the user. The brief ends with a **Touch-Points** section: the concrete files and resources you'd modify to add a feature to this subsystem.

## Args

- `/jarvis-study <topic>` — produce or load brief for this topic
- `/jarvis-study --refresh <topic>` — force regenerate, ignore cache
- `/jarvis-study --list` — list cached subsystem briefs
- `/jarvis-study` (no args) — list cached briefs and prompt for topic

Topic is free-form prose. The skill slugifies it for the filename ("membership management" → `membership-management`).

## Preamble

```bash
JARVIS_DIR="${JARVIS_DIR:-$HOME/.claude/skills/jarvis}"
VERSION=$(cat "$JARVIS_DIR/VERSION" 2>/dev/null || echo "0.0.0")
echo "JARVIS_VERSION: $VERSION"

# --- arg parsing ---
TOPIC=""
REFRESH=0
LIST=0
for arg in "$@"; do
  case "$arg" in
    --refresh|-r) REFRESH=1 ;;
    --list|-l)    LIST=1 ;;
    --help|-h)    echo "usage: /jarvis-study [--refresh|--list] <topic>"; exit 0 ;;
    -*) ;;
    *) TOPIC="${TOPIC:+$TOPIC }$arg" ;;
  esac
done

# --- slugifier ---
slug_of() {
  echo "$1" | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//'
}
SLUG=$(slug_of "$TOPIC")

# --- cache layout ---
mkdir -p .jarvis/subsystems
CACHE_FILE=".jarvis/subsystems/${SLUG}.md"

# --- AWS (optional — brief is more useful with live state but not required) ---
if AWS_ID=$(aws sts get-caller-identity --output json 2>/dev/null); then
  ACCOUNT=$(echo "$AWS_ID" | python3 -c 'import sys,json;print(json.load(sys.stdin)["Account"])' 2>/dev/null)
  REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-us-east-1}}"
  echo "AWS_ACCOUNT: $ACCOUNT"
  echo "AWS_REGION: $REGION"
  AWS_AVAILABLE=1
else
  echo "AWS_ACCOUNT: (not configured — brief will be code-only)"
  AWS_AVAILABLE=0
fi

# --- adoption status (advisory only — study runs without adoption) ---
if [ -f .jarvis/profile.json ]; then
  JARVIS_ADOPTED=1
else
  JARVIS_ADOPTED=0
  echo "NOTE: no .jarvis/profile.json — running in read-only project mode"
fi
```

## Step 0: Handle `--list` or empty topic

If `LIST=1`, enumerate cached briefs and exit:

```bash
if [ "$LIST" = "1" ]; then
  if compgen -G ".jarvis/subsystems/*.md" > /dev/null; then
    echo ""
    echo "Cached subsystem briefs:"
    for f in .jarvis/subsystems/*.md; do
      name=$(basename "$f" .md)
      mtime=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$f" 2>/dev/null \
              || stat -c "%y" "$f" 2>/dev/null | cut -d. -f1)
      lines=$(wc -l < "$f" | tr -d ' ')
      echo "  $name  ($mtime, ${lines} lines)"
    done
  else
    echo "No cached briefs. Run: /jarvis-study <topic>"
  fi
  exit 0
fi
```

If `TOPIC` is empty, list cached briefs (as above) and then use `AskUserQuestion` to prompt the user for the topic name. If they cancel, exit gracefully.

## Step 1: Cache + staleness check

If `CACHE_FILE` exists and `REFRESH=0`, decide whether to serve from cache.

A brief is **stale** if any file listed in its "Files in Scope" section has been modified after the brief's own mtime. Resolve like so:

```bash
if [ -f "$CACHE_FILE" ] && [ "$REFRESH" = "0" ]; then
  CACHE_MTIME=$(stat -f "%m" "$CACHE_FILE" 2>/dev/null || stat -c "%Y" "$CACHE_FILE")
  STALE=0
  STALE_FILES=""
  # Extract "Files in Scope" section lines starting with "- "
  IN_SCOPE=$(awk '
    /^## Files in Scope/ {flag=1; next}
    /^## / {flag=0}
    flag && /^- / {sub(/^- /,""); print}
  ' "$CACHE_FILE")

  while IFS= read -r f; do
    [ -z "$f" ] && continue
    if [ -f "$f" ]; then
      FM=$(stat -f "%m" "$f" 2>/dev/null || stat -c "%Y" "$f")
      if [ "$FM" -gt "$CACHE_MTIME" ]; then
        STALE=1
        STALE_FILES="${STALE_FILES}\n  - $f"
      fi
    fi
  done <<< "$IN_SCOPE"

  if [ "$STALE" = "0" ]; then
    echo ""
    echo "Cached brief is fresh: $CACHE_FILE"
    echo "(Run with --refresh to force regeneration.)"
    echo ""
    cat "$CACHE_FILE"
    exit 0
  else
    echo ""
    echo "Cached brief is stale — files changed since last study:"
    echo -e "$STALE_FILES"
    echo ""
    echo "Refreshing..."
  fi
fi
```

If you reach this point you must regenerate (no cache, stale cache, or `--refresh`).

## Step 2: Spawn the discovery agent

This is where thoroughness lives. Use the `Agent` tool with `subagent_type: "general-purpose"` (needs read + grep + bash + write). The agent runs the full discovery recipe and writes the brief to `CACHE_FILE`.

Pass it the variables: `TOPIC`, `SLUG`, `CACHE_FILE`, `AWS_AVAILABLE`, `ACCOUNT`, `REGION`, and the current working directory.

**Agent prompt template** (render with the variables and send via `Agent`):

```
You are the Jarvis "study" sub-agent. Produce a thorough subsystem brief for
the topic: "{TOPIC}".

Project root: {PWD}
Output file:  {CACHE_FILE}
AWS account:  {ACCOUNT or "(not available)"}
AWS region:   {REGION}
AWS scans available: {AWS_AVAILABLE: 1 or 0}

The user invokes this before adding a feature to the subsystem. The brief must
leave a fresh agent (with zero prior context) ready to:
  1. Understand the subsystem end-to-end.
  2. Know exactly which files/resources to touch for common changes.
  3. Avoid all past-incident mistakes documented in CLAUDE.md.
  4. Know which IAM/VPC/permissions a new resource will require.

# Discovery recipe — DO ALL OF THESE

Be thorough. The user has explicitly asked that nothing be missed. Cast a wide
net first, then narrow. Skipping a layer is the failure mode.

## Layer 1 — Project orientation
1. Read CLAUDE.md fully. Note every section, heading, and incident report
   that mentions the topic, its synonyms, or its tables/buckets/services.
2. Read README.md, ARCHITECTURE.md, and any docs/*.md that reference the
   topic.
3. Identify the project's structural conventions (where routes live, where
   services live, where tests live, where IaC lives).

## Layer 2 — Code surface (be exhaustive)
For each layer below, grep with multiple synonyms of the topic (e.g., for
"membership management": membership, subscription, tier, plan, billing,
credits, stripe, signup, signin, login, auth, user_management). Then:

4. **API routes**: every route file under api/, routes/, endpoints/.
   For each match: METHOD, path, auth requirement, file:line, one-line purpose.
5. **Services / business logic**: every service file. For each: class/function,
   file:line, one-line purpose.
6. **Schemas / Pydantic models / DTOs**: every relevant model.
7. **Middleware, decorators, dependencies**: anything that gates or enriches
   the subsystem (auth middleware, tier gating, rate limits).
8. **Background jobs / cron / workers / Step Function states / Lambdas**:
   anything that runs async or scheduled for this subsystem.
9. **Tests**: unit + integration tests for these flows. File paths.
10. **Migration / one-off scripts / provisioning scripts** (e.g., tmp scripts
    referenced in CLAUDE.md, scripts in scripts/, bash provisioning blocks).
11. **Frontend integration points** if the project has a frontend dir or
    the API exposes specific contracts (note expected request/response shapes).

## Layer 3 — Data surface
12. **DynamoDB tables**: which tables this subsystem reads/writes. Pull
    keys + GSIs from IaC (iac/**/*.tf) AND verify against live AWS if
    AWS_AVAILABLE=1 (`aws dynamodb describe-table --table-name X`).
13. **S3 buckets / prefixes** touched.
14. **Secrets** (Secrets Manager / .env / hardcoded — flag any hardcoded as
    a gotcha).
15. **Cache / Redis / OpenSearch** if used.

## Layer 4 — Infrastructure surface
16. **IaC files** (Terraform) defining or referencing the resources from
    Layer 3. Path per file with one-line purpose.
17. **IAM policies** that grant access to these resources. Which roles
    have them? If AWS_AVAILABLE=1, verify with
    `aws iam list-role-policies --role-name <role>` and
    `aws iam get-role-policy --role-name <role> --policy-name <name>`.
18. **VPC endpoints** that this subsystem's AWS API calls require (cross-
    reference CLAUDE.md's "Production VPC Endpoints (Required)" list).
19. **Step Functions / EventBridge / SQS / SNS** that fire for this
    subsystem.
20. **ALB / API Gateway / CloudFront** routing rules if applicable.

## Layer 5 — Cross-cutting concerns
21. **Auth flow**: how does a request authenticate against this subsystem?
    JWT? API key? Both?
22. **Billing / credit deduction**: where credits are charged or refunded
    for this subsystem.
23. **Email / SMS / Notifications** sent by this subsystem (template names,
    sender addresses, SES identities).
24. **External integrations**: Stripe, Gemini, OpenAI, Bedrock, Lob,
    Twilio, Collov, etc. Which API keys, which endpoints.
25. **Frontend contract**: required fields, naming conventions
    (camelCase vs snake_case), known frontend bugs (see CLAUDE.md for
    "Frontend Responsibility" notes).

## Layer 6 — Conventions & invariants
26. Patterns the codebase enforces here (naming, required fields, tenant
    isolation, slug rules, ID prefixes like `stg-job-`, `ref-lead-`, etc.).
27. Idempotency / dedup keys.
28. Status / lifecycle enums and valid transitions.

## Layer 7 — Past incidents & gotchas (mine CLAUDE.md hard)
29. Scan CLAUDE.md for headings containing "Fix", "Problem", "Incident",
    "CRITICAL", "Lesson Learned", "Gotcha", "Bug", "Issue", "Fixed".
    For each one related to this subsystem, capture: the problem, the root
    cause, the fix, and what to NEVER do again.
30. Scan `git log --all --oneline -- <file>` for files in scope; surface
    bug-fix commits.
31. Inspect recent code comments containing "TODO", "FIXME", "HACK",
    "XXX", "WORKAROUND" within in-scope files.

## Layer 8 — Activity & freshness
32. `git log --since="90 days ago" --oneline -- <in-scope files>` — list
    last 20 commits touching this subsystem.
33. List open TODO/FIXME comments still in code.
34. List known gaps mentioned in CLAUDE.md (look for "TODO", "Known
    Limitations", "Future Considerations").

## Layer 9 — Touch-point synthesis (THE KILLER OUTPUT)
35. Based on everything above, derive 3–6 common "add a feature here"
    scenarios. For each: enumerate the exact files, IaC modules, IAM
    policies, VPC endpoints, and tests a developer would touch.
    Be specific — give file:line where possible.

# Output format

Write the brief to `{CACHE_FILE}` using the exact template below. Use real
data — no placeholders, no "TODO: fill in". If you can't determine a section,
write "(none found)" rather than omit it; an empty section is a signal.

```markdown
# Subsystem Brief: {Topic title-cased}

**Slug:** {SLUG}
**Generated:** {ISO-8601 UTC}
**Project root:** {pwd}
**AWS account:** {ACCOUNT or "(not available)"}
**AWS region:** {REGION}

---

## TL;DR
{2–4 sentences: what this subsystem does, who calls it, the major
resources it owns, and the single most important gotcha to remember.}

---

## 1. Resources

### DynamoDB tables
| Table | Hash / Range | GSIs | Purpose | Source (IaC file) |
|---|---|---|---|---|

### S3 buckets / prefixes
| Path | Purpose | Source |
|---|---|---|

### Lambda functions
| Function | Trigger | Purpose | Source |
|---|---|---|---|

### Step Functions / EventBridge / SQS / SNS
| Resource | Type | Purpose | Source |
|---|---|---|---|

### Secrets & config
| Name | Type | Consumed by | Notes |
|---|---|---|---|

### VPC endpoints relied on
- list with rationale (cross-reference CLAUDE.md endpoint table)

---

## 2. Code surface

### API routes
| Method | Path | Auth | File:line | Purpose |
|---|---|---|---|---|

### Services
| File:symbol | Purpose |
|---|---|

### Schemas / models
| File:symbol | Purpose |
|---|---|

### Middleware / decorators
- list

### Background jobs / cron / workers
- list

### Tests
- list

### One-off scripts / migrations
- list

### Frontend integration points
- list (request/response shape gotchas)

---

## 3. IAM permissions required
| Policy name | Role | Resources | Source |
|---|---|---|---|

If AWS verified, mark each row "✓ verified" or "✗ missing in live AWS".

---

## 4. Conventions & invariants
- Bullet list with one-line rationale each.

---

## 5. External integrations
| Service | What it does | Where called | Credentials source |
|---|---|---|---|

---

## 6. Gotchas & past incidents
| Date | Incident | Root cause | What to avoid |
|---|---|---|---|

Pull aggressively from CLAUDE.md. Include the section title in source.

---

## 7. Recent activity (last 90 days)
- `abcdef0` 2026-MM-DD: subject (author)
- ...

## 8. Open TODOs / known gaps
- file:line — text

---

## 9. Touch-points for new features

For each scenario, list every file/resource a developer must touch.

### Scenario A: {e.g., "Add a new subscription tier"}
- Modify: `path/to/file.py:line` — what changes
- Add: `path/to/new_file.py` — purpose
- IaC: `iac/dynamodb/...` if a new table
- IAM: new policy `Allow{X}TableAccess` template
- VPC: only if a new AWS service is introduced (see Layer 4)
- Tests: `tests/...`
- Frontend contract: required fields to add

### Scenario B: ...
### Scenario C: ...
(3–6 scenarios, picked from the most common changes this subsystem sees.)

---

## 10. Cheatsheet

A 6–10 line copy-pasteable summary an agent can paste into a future prompt
to be primed without reading the whole brief. Just the essential names,
paths, and invariants.

---

## Files in Scope
List every file path that contributed to this brief, one per line, leading
with "- ". This list drives cache invalidation — if any of these files
changes, the brief becomes stale.

- path/one
- path/two
- ...
```

# Rules

- Be exhaustive. Skipping a layer is the failure mode.
- When AWS_AVAILABLE=1, verify IaC claims against live state (table schemas,
  IAM policies). Mark mismatches explicitly — drift is information.
- Do not invent. If you can't find something, write "(none found)" — but only
  after searching with multiple synonyms.
- The "Files in Scope" list must be complete. The skill uses it for cache
  invalidation, so anything you read should appear there.
- The "Touch-points" section is the highest-value section. Spend extra time
  on it. Be concrete — file:line where you can.
- The "Cheatsheet" must be self-contained: an agent reading only that 10-line
  block should be able to start work safely.

Return a single message: "Brief written to {CACHE_FILE}. {N} files in scope.
Scenarios surfaced: {list}."
```

## Step 3: Display the brief

After the discovery agent finishes:

```bash
# Sanity check: file exists and is non-trivial
if [ ! -f "$CACHE_FILE" ] || [ "$(wc -l < "$CACHE_FILE")" -lt 30 ]; then
  echo "ERROR: brief was not written or is suspiciously short. Re-run with --refresh."
  exit 1
fi

echo ""
echo "Brief saved: $CACHE_FILE"
echo ""
```

Then print to the user (not via `cat` — use a text response):
1. The TL;DR (section 1)
2. The list of section headings with line counts
3. The Cheatsheet (section 10) verbatim
4. A one-line pointer: "Full brief: $CACHE_FILE"

Do NOT dump the whole brief to chat — it can be long. The user reads the file when they want detail; chat gets the summary.

## Step 4: Telemetry / done

Report `DONE` with: topic, slug, file path, # files in scope, # scenarios surfaced. If something failed (agent returned no file, AWS check denied, etc.), report `BLOCKED` with the specific reason and recommend `--refresh` or `aws configure`.

## Maintenance notes

- The cache lives in `.jarvis/subsystems/` (gitignored by default if `.jarvis/` is in `.gitignore`; otherwise the user can commit them to share with the team).
- Staleness is file-mtime based. Acceptable false-positive rate. If users complain about over-refreshing, add a content-hash mode later.
- The discovery recipe in Step 2 is the contract. Update it when the project gains new layers (e.g., a new AWS service worth checking).
- This skill is read-only on the codebase. It only writes to `.jarvis/subsystems/<slug>.md`. It must never edit application code or IaC.
