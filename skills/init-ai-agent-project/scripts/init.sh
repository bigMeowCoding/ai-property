#!/usr/bin/env bash
# Stable shell entry point for the profile-aware Python initializer.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/init_project.py" "$@"
