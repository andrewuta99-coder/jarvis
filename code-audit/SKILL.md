---
name: jarvis-code-audit
version: 0.1.0
description: |
  Line-by-line code audit against Google Style Guides and Anthropic's
  engineering principles. Catches duplicated code, dead code, missing types,
  O(n²) inefficiencies, deeply nested logic, god classes, magic numbers,
  long functions, missing tests, architectural violations (circular imports,
  layering breaks), and naming inconsistencies. Produces an actionable report
  ranked by severity with file:line citations and concrete fixes. (jarvis)
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
triggers:
  - jarvis code audit
  - code audit
  - audit my code
  - review every line
  - quality check
  - is my code clean
---

# /jarvis-code-audit — Line-by-line code review

Reviews the working tree against a fixed standard derived from:

- **Google Style Guides** (python, javascript, typescript, go, html/css)
- **Anthropic engineering principles**: clarity over cleverness, fail loudly,
  explicit > implicit, no premature abstractions, names that describe behavior
- **Algorithmic hygiene**: O(n²) where O(n) is possible, repeated lookups
  where caching would help, missing indexes on hot paths

The output is one markdown report per audit run, dropped at
`.jarvis/audits/code-<ISO_DATE>.md`, with a final ship-readiness score.

## When to run this

| When | Why |
|---|---|
| Before merging a feature branch | Pre-landing checks |
| Quarterly on the whole repo | Drift control |
| When onboarding to an unfamiliar repo | Map smells before adding features |
| After a major refactor | Verify the refactor improved measurable quality |

## How it runs

```bash
~/.claude/skills/jarvis/bin/jarvis-code-audit \
  --target-dir <repo>            # default: cwd
  --since main                   # only audit files changed vs main
  --languages python,typescript  # default: auto-detect
  --output .jarvis/audits/        # default
  --max-files 200                # default; safety cap on huge repos
  --strict                       # treat MAJOR as failing
```

For the conversational version, the agent invokes the bin and then walks
the report with the user.

## What the bin checks

### 1. Static analysis (per language)

| Language | Tools the bin tries (skips if missing) |
|---|---|
| Python | `ruff check --select=ALL`, `mypy --strict`, `radon cc -a`, `vulture` |
| TypeScript / JS | `tsc --noEmit`, `eslint`, `jscpd` |
| Terraform | `terraform fmt -check`, `tflint`, `checkov` |
| Shell | `shellcheck` |

If a tool is missing the audit notes "tool not installed, would have run X"
but does not fail — degrades gracefully.

### 2. Universal smell detection (regex + AST)

Runs regardless of language:

- **Duplication**: identical line-runs of length ≥ 10 across the codebase
- **God files**: > 500 lines
- **God functions**: > 50 lines or cyclomatic complexity > 10
- **Deep nesting**: > 4 levels of indentation in a single function
- **Magic numbers**: numeric literals other than 0, 1, -1, 100, 1024, 60 in
  non-test code without a named constant nearby
- **Unused imports**: per language
- **Dead code**: functions defined but never referenced from outside their file
- **Long parameter lists**: > 5 params
- **TODO / FIXME / XXX**: catalogued (not flagged as issues per se, but listed
  so the team knows what's pending)

### 3. Algorithmic hygiene

A pattern matcher looking for known-slow shapes:

- **Nested loops over the same collection**: classic O(n²)
- **`.find()` / `.includes()` inside `.map()` / `.forEach()`**: O(n²)
- **Repeated DB calls inside loops**: N+1 query smell
- **Repeated `JSON.parse(JSON.stringify(x))`**: deep-clone with poor performance
- **String concatenation inside loops in Python**: should be `''.join()`
- **Recursive functions without memoization** where the recursion tree has
  overlapping subproblems

For each match, the bin proposes the optimized form:
```python
# BEFORE
for user in users:
    if any(o["user_id"] == user["id"] for o in orders):  # O(n*m)
        active.append(user)

# AFTER
order_user_ids = {o["user_id"] for o in orders}            # O(m)
active = [u for u in users if u["id"] in order_user_ids]   # O(n)
```

### 4. Architecture checks

- **Circular imports** between modules
- **Layering violations**: `data/` importing from `api/`, `models/`
  importing from `services/`, etc. (configurable per project)
- **Tight coupling**: a class importing > 10 other modules
- **God classes**: > 7 public methods, > 5 fields
- **Missing tests**: source files with no corresponding test file
- **Coverage gaps**: function exists in source but has 0 lines covered

### 5. Naming + readability

- Names that contain `data`, `info`, `obj`, `tmp`, `manager`, `helper` without
  a noun ("X manager of what?")
- Variables one character long (except `i`, `j`, `k` in loops, `x`, `y`, `z`
  in geometry)
- Functions that don't start with a verb
- Booleans that don't start with `is_`, `has_`, `should_`, `can_`, `will_`
- Inconsistent naming styles within the same file (camelCase + snake_case
  mixed)
- Comments that describe WHAT the code does (should describe WHY)

## Severity scale

| Severity | Examples | Action |
|---|---|---|
| **CRITICAL** | Security-adjacent (use `/jarvis-security-audit` for full coverage), data loss risk, O(n³) on hot paths | Block merge |
| **MAJOR** | God classes, duplicated logic ≥ 30 lines, missing types on public APIs, no tests for new features | Fix before merge |
| **MINOR** | Magic numbers, long parameter lists, dead code | Cleanup batch |
| **NIT** | Naming style inconsistencies, comment quality | Optional |

The bin's exit code: 0 if no MAJOR or CRITICAL, 1 otherwise.

## Report format

```markdown
# Code Audit — {{REPO_NAME}}
Generated: 2026-06-14T12:00:00Z
Audit window: HEAD vs main (47 files changed)
Score: 78/100 (B+)

## Summary
- 2 CRITICAL — must fix before merge
- 7 MAJOR — should fix
- 14 MINOR — cleanup batch
- 23 NIT — optional

## CRITICAL

### C1. O(n²) lookup in checkout flow
**File**: `real_estate_service/services/orders/checkout.py:147`
**What**: `.find()` inside `.forEach()` over the cart items.
**Impact**: At 100 items per cart, this is 10,000 ops per checkout call.
**Fix**: Build a `{id: item}` dict before the loop.
**Confidence**: high — clear pattern, deterministic improvement.

### C2. Bare `except` swallowing payment errors
**File**: `real_estate_service/services/payments/webhook.py:88`
**Why critical**: Errors silently absorbed; failed webhooks won't retry.

## MAJOR
...

## MINOR
...

## Architecture observations
- Circular import detected: `data/users.py` ↔ `services/auth.py`
- `services/leads_service.py` has 23 imports — consider splitting
- 18 source files have no test file pair

## Style guide deviations
...

## TODOs catalogued (47)
...

## What to do next
1. Fix the 2 CRITICAL items today.
2. Open a tracking issue for the 7 MAJOR; ship as a follow-up PR.
3. Park MINOR in a tech-debt backlog.
```

## How the agent walks the report

When the user runs `/jarvis-code-audit`, the agent should:

1. Run the bin in the project root.
2. Read the report.
3. **Surface the CRITICAL items inline** with the user — show the actual
   code, propose the fix, ask "want me to apply this?"
4. For MAJOR items, group them and ask whether to fix in this session
   or write a tracking doc to revisit.
5. Skip MINOR / NIT unless asked — they pollute the conversation.
6. End with the score + one paragraph: "Your stack is at 78/100. The two
   CRITICAL items are local to checkout.py. Fixing them takes ~15 minutes
   and bumps you to ~90."

## Anti-patterns the agent must avoid

- **Do not list every NIT in chat.** They go in the file. Surface them
  only on `--strict` mode or explicit ask.
- **Do not invent rules.** Every flagged issue must trace back to a real
  Google style guide line, an Anthropic engineering principle the project
  already follows, or a measurable performance/security concern.
- **Do not "fix" code the user didn't ask to fix.** Propose, ask, then act.
- **Do not flag stylistic preferences as defects.** "I'd format it this way"
  is not a finding.

## Voice

> Hot spot: `checkout.py:147` has an `.find()` inside a `.forEach()` over the
> same cart items. At 100 items per cart that's 10,000 ops per call. Two-line
> fix: build a `{id: item}` dict outside the loop, then look up. Want me to
> apply it?
