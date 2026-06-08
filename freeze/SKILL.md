---
name: jarvis-freeze
version: 0.0.1
description: |
  Restrict file edits to one directory for the rest of the session. Prevents
  accidental "fixes" outside the scope you're working in. Pairs with /jarvis-careful. (jarvis)
allowed-tools: [Bash, AskUserQuestion]
triggers: [jarvis freeze, lock edits, freeze]
---

# /jarvis-freeze — scoped edit lock

Pin your edit scope to one directory. Useful when debugging a feature and you don't want the agent to "helpfully" edit unrelated code.

## Activation

Ask which directory:

> Freeze edits to which path?
>   A) Current working directory ({{cwd}})
>   B) iac/ only
>   C) backend/ only
>   D) frontend/ only
>   E) A specific subdirectory (type below)

Write the choice to `.jarvis/freeze.txt` and set the config flag:

```bash
echo "$PATH" > .jarvis/freeze.txt
~/.claude/skills/jarvis/bin/jarvis-config set freeze_path "$PATH"
```

## Enforcement

The Claude Code skill preamble in every Jarvis skill checks `freeze_path` and refuses Edit/Write operations outside it.

```bash
FREEZE=$(jarvis-config get freeze_path 2>/dev/null)
if [ -n "$FREEZE" ] && [ "$FREEZE" != "false" ]; then
  echo "FROZEN: $FREEZE"
fi
```

When `FROZEN` is set, any skill that's about to Edit/Write must check the target path. If outside the freeze, halt with:

> BLOCKED: /jarvis-freeze is active. Cannot edit {{TARGET}}.
> Allowed scope: {{FREEZE}}
> To widen: run /jarvis-unfreeze.

## Deactivate

```bash
~/.claude/skills/jarvis/bin/jarvis-config set freeze_path false
rm -f .jarvis/freeze.txt
```

Or run `/jarvis-unfreeze` (not implemented as a separate skill at v0 — just config set).

## Companion

`/jarvis-careful` adds destructive-command warnings on top. `/jarvis-guard` activates both.
