---
name: jarvis-prototype
version: 0.1.0
description: |
  PM-to-clickable-React skill. Turn a one-liner ("leads kanban for loan
  officers") or a /jarvis-pm spec into a working, beautiful React
  prototype the team can click through — using the project's existing
  conventions (CRA/Next/Vite + Tailwind + lucide-react + react-router,
  whatever the repo already uses) so engineering can keep what works.
  Mock data is inline, routes are isolated, no backend required.
  Picks a curated design system if DESIGN.md is absent. Designed so a
  non-technical PM can ship a polished demo URL in under 10 minutes. (jarvis)
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
triggers:
  - jarvis prototype
  - build me a prototype
  - prototype this feature
  - mock up a UI
  - fast UI
  - make a demo page
  - clickable demo
  - turn my idea into a UI
  - quick wireframe in code
---

# /jarvis-prototype — PM-to-clickable-React in minutes

A non-technical PM has an idea ("a kanban board for our loan officers"
or "a landing page for the new flow") and wants a **polished, clickable
prototype** the team can react to today. This skill produces React code
that:

1. **Matches the project's existing stack** — detects CRA / Next / Vite,
   Tailwind / CSS modules, lucide-react / heroicons, react-router /
   next/router, theme context, file layout. Generates code that drops in.
2. **Looks intentional, not generic** — picks (or accepts) a complete
   design system: typography (Google Fonts pair), color tokens, motion,
   spacing, anti-patterns. Beautiful out of the box.
3. **Routes to a clean isolated page** — no app routing surgery; just a
   new route prefixed `/prototypes/<slug>` plus a banner so it's clear
   the data is mocked. Engineering decides later whether to keep, fork,
   or rewrite.
4. **Carries mock data inline** — no API calls, no env vars, no auth.
   The PM clicks `npm start` and demos.
5. **Self-documents** — every generated page has a comment block at the
   top: which spec it came from, which style profile was used, what's
   mocked, what to wire next.

## What the PM gets out the door

```
<frontend_root>/
├── src/prototypes/<slug>/
│   ├── README.md                  one-page summary for engineers
│   ├── <Slug>Page.jsx             the routable page
│   ├── components/                supporting components (cards, modals, etc.)
│   ├── mock-data.js               inline fixtures so it runs without backend
│   └── styles.js                  the resolved design tokens (for reuse)
└── (optional) one-line router patch suggesting `/prototypes/<slug>`
```

After running, the PM can:
- `npm start` (or whatever the project uses), navigate to `/prototypes/<slug>`
- Walk a stakeholder through the flow with real-looking data
- Hand it to engineering with the README; engineers know exactly what's
  mocked vs. what needs wiring

## When to use this

| When | Why |
|---|---|
| Stakeholder wants to "see it" before scoping | Faster than Figma, real React |
| `/jarvis-pm` produced a spec — show it working | Closes the spec→prototype gap |
| Exploring 2-3 layout options | Run the skill 2-3 times with different `--style` |
| Designer is busy and PM is unblocked | Doesn't replace design — primes the conversation |
| Pitch deck demo | Live URL beats screenshots |

**Not for:** production code, authenticated flows, anything talking to
real APIs, or anything the user will ship without engineering review.
The generated banner makes the mock status loud on purpose.

## How to invoke

```
/jarvis-prototype "leads kanban for loan officers"
/jarvis-prototype --from-spec .jarvis/pm/leads-kanban/SUMMARY.md
/jarvis-prototype "checkout flow" --style ecommerce-vivid
/jarvis-prototype "investor dashboard" --route /demo/investor --page-name InvestorDemo
/jarvis-prototype --list-styles
```

Flags (all optional):
- `<description>` — one-line product description (positional)
- `--from-spec <path>` — read a `/jarvis-pm` SUMMARY.md and use it
- `--style <id>` — pick a curated profile by id (e.g. `mortgage-lender`,
  `clean-saas`, `ai-product`); run `--list-styles` to see all
- `--page-name <Name>` — override the React page component name
- `--route <path>` — override the route (default `/prototypes/<slug>`)
- `--frontend-dir <path>` — override frontend root detection
- `--ts` / `--js` — force TypeScript or JavaScript output (default: match repo)
- `--screenshots` — after generation, navigate the browse tool to the URL
  and capture a 1280x800 screenshot for sharing

## The five phases

### Phase 1 — Discovery (run before anything else)

```bash
~/.claude/skills/jarvis/bin/jarvis-prototype discover \
  --frontend-dir "${FRONTEND_DIR:-.}"
```

This emits a JSON discovery report describing the frontend stack:

```json
{
  "found": true,
  "frontend_root": "/path/to/repo",
  "framework": "cra | next | vite | unknown",
  "language": "ts | js",
  "styling": {
    "tailwind": true,
    "tailwind_config_path": "tailwind.config.js",
    "custom_theme_colors": {"brand": "#0F766E"},
    "css_modules": false
  },
  "icons": "lucide-react | @heroicons/react | react-icons | none",
  "routing": "react-router-dom@6 | next-app-router | next-pages | none",
  "state": ["ContextAPI", "Zustand", "Redux"],
  "components_dir": "src/lender/components",
  "pages_dir": "src/lender/pages",
  "design_md_path": "DESIGN.md | null",
  "design_md_present": true,
  "theme_context_path": "src/lender/contexts/ThemeContext.js | null",
  "existing_components": ["Button", "Card", "Modal", "..."]
}
```

If `found: false`, ask the PM where the React app lives. Don't guess —
generating into the wrong directory is worse than asking.

### Phase 2 — Read the spec / description

Resolve `description` in this priority order:

1. `--from-spec <path>` → read that markdown, distill into:
   - **Persona** (who the user is)
   - **Job-to-be-done** (what they're trying to accomplish)
   - **Top 3 screens** (landing, primary action, success/empty states)
   - **Top 3 user flows** (steps for the most-used path)
   - **Key data shapes** (entities, fields)
2. Positional `<description>` → ask 3 focused questions to fill the gaps:
   - "Who is the user (one role)?"
   - "What are the top 2-3 things they need to do on this screen?"
   - "What data do they look at most (one sentence)?"

Don't over-interview. If the PM gives sparse answers, infer reasonable
defaults and surface them in the generated README so the PM can correct.

### Phase 3 — Resolve the design system

This is the taste decision. Run in this order:

**3a. Project's own design system (highest priority)**

If `discovery.design_md_present` is true, READ `DESIGN.md` and extract:
- Typography (font families and weights to load)
- Color tokens (primary, accent, neutral scale, semantic colors)
- Spacing scale
- Radius scale
- Motion (durations, easings)
- Component conventions (button styles, card styles)

Use exactly these tokens. Do not introduce new colors or fonts.

**3b. Tailwind config (if no DESIGN.md)**

If `discovery.styling.custom_theme_colors` is non-empty, use those as
the brand palette. Pair with a sensible neutral scale (slate or zinc)
and Inter as the default sans.

**3c. Curated style profile (fallback)**

If neither exists, pick a profile from
`~/.claude/skills/jarvis/prototype/styles.json`. Match by `best_for`
against the product description.

| If the description mentions... | Default to |
|---|---|
| "mortgage", "loan", "underwriting", "lender", "CloudMortgage" | `mortgage-lender` |
| "real estate", "realtor", "listing", "property", "open house" | `realtor-warm` |
| "AI", "chat", "assistant", "LLM", "agent" | `ai-product` |
| "dashboard", "analytics", "monitor", "ops" | `dashboard-dense` |
| "bank", "fintech", "invest", "credit", "tax" | `fintech-trust` |
| "B2B SaaS", "admin", "internal tool", "workspace" | `clean-saas` |
| "ecommerce", "store", "checkout", "product catalog" | `ecommerce-vivid` |
| "patient", "telehealth", "wellness", "clinic" | `healthcare-calm` |
| "education", "course", "tutoring", "LMS" | `education-friendly` |
| "developer", "CLI", "logs", "infra" | `devtools-terminal` |
| "fitness", "workout", "sports" | `fitness-energy` |
| "law", "compliance", "audit", "contract" | `legal-formal` |
| "portfolio", "agency", "case study" | `creative-portfolio` |
| "blog", "essay", "documentation", "reading" | `minimal-text` |
| "mobile", "PWA", "phone-first" | `mobile-first` |
| "luxury", "premium", "hospitality", "spa", "estate" | `luxury-marketing` |
| (default) | `clean-saas` |

Confirm the choice with the PM in **one line** before generating:

> Picked the **{style.name}** profile (looks great for {best_for[0]}).
> Want a different vibe? Run with `--style <id>` — see all with
> `/jarvis-prototype --list-styles`.

Don't trap the PM in a style interview. The right move is "show them
the prototype fast; they can re-run with a different style if they hate it."

### Phase 4 — Generate

Decide file layout from discovery:
- `pages_dir`: `discovery.pages_dir` or `src/pages` or `app/`
- `components_dir`: `discovery.components_dir` or `src/components`
- Prefer the convention seen in nearby files (e.g. if the project uses
  `src/lender/pages/`, drop the prototype at `src/lender/pages/PrototypeName.jsx`)

Generate this exact file tree:

```
src/prototypes/<slug>/
├── README.md           — engineer-facing: spec source, style id, what's mocked
├── <Slug>Page.{jsx,tsx} — the routable page; uses internal components only
├── components/
│   ├── <Component1>.{jsx,tsx}
│   ├── <Component2>.{jsx,tsx}
│   └── ...
├── mock-data.{js,ts}    — typed fixtures for all entities
└── styles.{js,ts}       — exports the resolved design tokens
```

If the project uses `src/lender/`, `src/borrower/`, etc., **scope the
prototype to one of those** based on the spec's persona, OR place it at
`src/prototypes/` (universal). Default to `src/prototypes/` to avoid
treading on team-owned directories.

#### React generation rules

These rules are non-negotiable. Write them into the generation prompt
when fanning out via the Agent tool, and verify after generation.

**Structure**
- Functional components only. No class components.
- Default-export the page; named-export everything else.
- One component per file. No barrel files unless the project already uses them.
- Hooks at the top of the function body; helpers below.
- No `useEffect` for derived data — use a `useMemo` instead.

**Styling**
- Tailwind only if `discovery.styling.tailwind` is true.
- If Tailwind, use **arbitrary value syntax** for the style profile's
  exact color tokens: `bg-[#0F766E]` rather than guessing the nearest
  Tailwind blue. This guarantees the design profile is respected.
- Spacing comes from the profile's scale; no random numbers.
- All interactive elements need a visible focus state (`focus-visible:ring-2`).
- All touch targets ≥ 40x40px (44 on mobile-first profiles).
- Dark/light: respect `discovery.theme_context_path` if present.

**Typography**
- Add the profile's `google_fonts_url` `<link>` to `index.html` ONLY if
  not already present. Otherwise add a comment in `<Slug>Page` listing
  the fonts and tell the PM to add them in the README.
- Use the profile's display font for `h1` and key metrics; body font
  everywhere else.

**Icons**
- Use `discovery.icons` if non-`none`. Otherwise default to
  `lucide-react` (most projects either already use it or are happy to).
- Don't mix icon libraries.

**Mock data**
- 8-25 records per entity. Vary realistically: real-looking names,
  varied dates, varied statuses, varied amounts.
- Include edge states: at least one record showing empty, one showing
  "loading-like" placeholder, one showing error/danger styling.
- Export a typed shape (`/** @typedef {{...}} Lead */` in JS,
  proper interface in TS).

**State**
- Local `useState` only. No external state libraries — even if the
  project uses Redux/Zustand. The prototype must be self-contained.
- Use `useReducer` for anything with > 4 state variables.

**Routing**
- Generate the `Route` element line, but **do not modify the app's
  router config file**. Instead, print a one-line patch suggestion in
  the report. The PM (or an engineer) can add it manually.

**Accessibility**
- Every `<img>` has an alt, every button has discernible text or
  `aria-label`, every form input has a label, color contrast ≥ 4.5:1
  for body text and ≥ 3:1 for large text and icons.

**Quality bar (the soul of the skill)**
- No "lorem ipsum." Use realistic, on-domain copy.
- No placeholder images from random services. Use a colored block with
  the entity's initial (or use `discovery.styling` patterns if the
  project has an avatar component).
- No empty hover states. Every interactive thing has a hover state.
- No bare `<table>` — always with proper `<thead>`, hover row, sticky header.
- No `console.log` left in code.
- Every page has a top-of-page banner: **"PROTOTYPE — mocked data, not
  production"** styled so it's impossible to miss in a screenshot.

#### The prototype banner (mandatory)

Every generated page MUST include this banner component at the top:

```jsx
<div className="bg-amber-50 border-b border-amber-200 px-4 py-2 text-sm text-amber-900 flex items-center justify-between">
  <span><strong>Prototype</strong> — mocked data, not production. Generated from spec: <code>{specSource}</code></span>
  <span className="text-xs opacity-70">Style: {styleId}</span>
</div>
```

Use the project's color palette for the banner if `mortgage-lender` or
similar trust-focused style is in play, but keep the words. The banner
is a safety guarantee — a designer or executive must never confuse this
with shipped product.

### Phase 5 — Verify and report

After generating, in this order:

1. **Typecheck** (if applicable):
   ```bash
   cd "$FRONTEND_ROOT" && npx tsc --noEmit 2>&1 | head -50
   ```
   If errors are in prototype files, FIX them — don't ship broken code.
2. **Lint** (if available):
   ```bash
   cd "$FRONTEND_ROOT" && npx eslint "src/prototypes/<slug>/**" 2>&1 | head -30
   ```
   Fix warnings in the generated files only. Don't touch unrelated lint debt.
3. **Build smoke test** (only if quick):
   ```bash
   cd "$FRONTEND_ROOT" && timeout 60 npm run build 2>&1 | tail -20 || true
   ```
   If build fails on the prototype, fix it. If build fails elsewhere,
   note it but don't block.
4. **Screenshot** (if `--screenshots`):
   - Start dev server in background
   - Use the gstack `/browse` skill or the project's browse tooling to
     navigate to `http://localhost:3000/prototypes/<slug>` and capture
     a 1280x800 PNG to `.jarvis/prototypes/<slug>/preview.png`

Final report to the PM:

```
✓ Prototype generated.

  Spec:       leads kanban for loan officers
  Style:      mortgage-lender (Inter + teal + slate)
  Files:      src/prototypes/leads-kanban/ (6 files)
  Components: LeadCard, KanbanColumn, FilterBar, EmptyState

To preview:
  cd <frontend_root>
  npm start
  open http://localhost:3000/prototypes/leads-kanban

To wire into the app router (one-line patch):
  // src/lender/App.js
  <Route path="/prototypes/leads-kanban" element={<LeadsKanbanPage />} />

What's mocked:
  - 14 leads with varied stages, sources, owners
  - Drag-and-drop is local-only (no persistence)
  - Filter bar shows UI but doesn't filter (intentional — design check first)

Next:
  - PM: walk a stakeholder through the flow
  - Engineering: read src/prototypes/leads-kanban/README.md before keeping/replacing
  - Run again with --style <id> for a different look
```

## Composing with other skills

- **Before:** `/jarvis-pm` to produce a spec → `/jarvis-prototype --from-spec`
- **After:** the gstack `/design-review` skill to audit the visual polish
- **Iteration:** run twice with two different `--style` to A/B feel

## Anti-patterns the skill must refuse

1. **No backend changes.** The prototype never touches the API, never
   adds a DynamoDB table, never modifies auth. Mocks only.
2. **No app router surgery.** Generate the `<Route>` snippet; let the PM
   or engineer paste it. Modifying the app's router is invasive and
   surprising.
3. **No new design tokens if DESIGN.md exists.** Use the project's
   system or you're undermining the team.
4. **No "I picked nice defaults."** Always name the style profile or
   DESIGN.md source in the generated README. Engineering should know
   exactly where every color came from.
5. **No silent overwrites.** If `src/prototypes/<slug>/` already exists,
   ask before overwriting (or pick a new slug).

## Failure modes and how to recover

| Failure | Recovery |
|---|---|
| Frontend not found | Ask PM where it is; offer `--frontend-dir` |
| Tailwind missing | Generate inline `<style>` block; warn that styles won't compose |
| TypeScript errors | Fix in-place. Re-run typecheck. If still broken, surface the error and ask the PM what to do. |
| Style profile id not found | List all profiles and ask |
| Existing prototype slug | Suggest `<slug>-v2` or `--page-name` |
| Build fails on unrelated files | Note in report, don't block — the prototype lives in an isolated dir |

## What this skill is NOT

- Not a Figma replacement. It's faster for clickable demos but worse
  for typography/spacing exploration.
- Not a production code generator. Mocks data, skips edge cases,
  skips auth.
- Not a design system generator. Use `/design-consultation` for that.
  This skill *consumes* a design system; it doesn't author one.
- Not a router. It writes the route snippet but doesn't wire it.
