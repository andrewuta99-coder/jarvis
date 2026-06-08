# Feature Templates

This is where the **invisible rails** live. Every per-feature template directory contains the hand-crafted Terraform, IAM, code, and tests that specialist sub-agents render and write to the user's project.

## Structure (per feature)

```
templates/features/<feature-name>/
├── manifest.yaml             # what this feature composes
├── terraform/                # Terraform partials (.tf.tmpl)
├── code/
│   ├── python/               # Python backend partials
│   └── typescript/           # TypeScript backend partials
├── frontend/
│   ├── react/                # CRA/Vite React components
│   └── nextjs/               # Next.js pages/components
├── tests/                    # integration test partials
└── docs/                     # docs/features/<feature>.md
```

## Adding a new feature

1. Create the directory under `templates/features/<name>/`
2. Write `manifest.yaml` listing the files this feature composes
3. Write template files with `.tmpl` extension and `{{SLOT}}` substitution
4. Add a corresponding user-facing skill at `<name>/SKILL.md` (or `add-<name>/SKILL.md`)
5. Add a specialist agent in `agents/<name>/SKILL.md` if this is a new domain
6. Add the feature to the AI SaaS starter manifest if it should ship by default

## Status

**v0 — scaffold only.** Each feature directory will be filled with concrete `.tmpl` files in upcoming milestones:

- v0.1: auth + ai + payments (the AI SaaS demo path)
- v0.2: email + files + jobs + frontend
- v0.3: realtime + phone + domain + remaining

This README is here so the directory structure ships from day one.
