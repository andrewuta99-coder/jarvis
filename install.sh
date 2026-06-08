#!/usr/bin/env bash
# Jarvis installer — one-liner install via curl.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/andrewuta99-coder/jarvis/main/install.sh | bash
#
# What it does:
#   1. Clone Jarvis to ~/.claude/skills/jarvis (or update if present)
#   2. Run ./setup to symlink skills into Claude Code (or another host)
#   3. Print next steps

set -e

REPO_URL="https://github.com/andrewuta99-coder/jarvis.git"
INSTALL_DIR="${JARVIS_INSTALL_DIR:-$HOME/.claude/skills/jarvis}"
HOST="${JARVIS_HOST:-claude}"

# Allow override via env or args
while [ $# -gt 0 ]; do
  case "$1" in
    --host)   HOST="$2"; shift 2 ;;
    --host=*) HOST="${1#*=}"; shift ;;
    --dir)    INSTALL_DIR="$2"; shift 2 ;;
    --dir=*)  INSTALL_DIR="${1#*=}"; shift ;;
    -h|--help)
      cat <<EOF
Jarvis installer

Usage: curl -fsSL https://raw.githubusercontent.com/andrewuta99-coder/jarvis/main/install.sh | bash

Options (via env vars or args):
  --host <name>   Target AI agent host (default: claude)
                  Supported: claude, codex, cursor, opencode, factory,
                             kiro, hermes, slate, gbrain, openclaw
  --dir <path>    Install directory (default: ~/.claude/skills/jarvis)

EOF
      exit 0
      ;;
    *) echo "Unknown flag: $1" >&2; exit 1 ;;
  esac
done

echo ""
echo "  Jarvis Installer"
echo "  ----------------"
echo ""

# Check prerequisites
if ! command -v git >/dev/null 2>&1; then
  echo "  ERROR: git is required but not installed." >&2
  echo "  Install git first: https://git-scm.com/" >&2
  exit 1
fi

if ! command -v bun >/dev/null 2>&1; then
  echo "  WARNING: bun is not installed (required for CLI binaries)."
  echo "  Install bun: curl -fsSL https://bun.sh/install | bash"
  echo "  Continuing without it — skills will work, CLI binaries will not build."
  echo ""
fi

# Clone or update
if [ -d "$INSTALL_DIR/.git" ]; then
  echo "  Found existing install at $INSTALL_DIR — updating..."
  ( cd "$INSTALL_DIR" && git pull --ff-only --quiet )
else
  if [ -e "$INSTALL_DIR" ]; then
    echo "  ERROR: $INSTALL_DIR exists but is not a git repo." >&2
    echo "  Remove it or pass --dir <other-path>." >&2
    exit 1
  fi
  echo "  Cloning Jarvis into $INSTALL_DIR..."
  mkdir -p "$(dirname "$INSTALL_DIR")"
  git clone --single-branch --depth 1 "$REPO_URL" "$INSTALL_DIR" --quiet
fi

# Run setup for the chosen host
echo "  Running setup for host: $HOST"
( cd "$INSTALL_DIR" && ./setup --host "$HOST" --quiet )

VERSION=$(cat "$INSTALL_DIR/VERSION" 2>/dev/null || echo "unknown")

cat <<EOF

  Done.

  Jarvis $VERSION installed to: $INSTALL_DIR
  Skills available in $HOST.

  Next steps:
    1. Open Claude Code (or your AI agent of choice)
    2. Run: /jarvis-init
    3. Follow the 4-question interview
    4. Watch your AWS app build itself in under 10 minutes

  Need AWS credentials first? Run: aws configure

  Trouble? Read the docs: https://github.com/andrewuta99-coder/jarvis
  Update later:           /jarvis-upgrade

EOF
