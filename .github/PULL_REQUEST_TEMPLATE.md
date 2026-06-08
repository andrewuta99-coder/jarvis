<!-- Thanks for the PR. Fill in the relevant sections; delete the rest. -->

## What changed

<!-- One sentence. What does this PR do? -->

## Why

<!-- One paragraph. The reason. If incident-derived, include date + symptom. -->

## How to verify

<!-- Reproducible steps so a reviewer can confirm the change works. -->

```bash
# example
./test/run_tests.sh
python3 bin/jarvis-render --feature <yours> --context test/fixtures/sample-context.json --target-dir /tmp/x --dry-run
```

## Checklist

- [ ] `./test/run_tests.sh` passes (19/19 or more)
- [ ] New / modified `.tmpl` files have the standard generated-by header
- [ ] `terraform fmt -check` on any new .tf templates
- [ ] CHANGELOG.md updated under "Unreleased"
- [ ] Manifests for new features declare `inputs`, `outputs`, exclusive `writes_glob`
- [ ] For incident-derived defaults: comment cites the date + symptom

## Type

<!-- Tick one -->
- [ ] feat (new capability)
- [ ] fix (bug)
- [ ] docs (docs only)
- [ ] template (new or updated template)
- [ ] starter (new starter manifest)
- [ ] chore (maintenance, deps, ci)

## Out of scope (closes #issue)

<!-- Link issues this closes. -->
