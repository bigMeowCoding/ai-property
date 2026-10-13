#!/usr/bin/env bash
# Stable shell entry point for the profile-aware workflow initializer.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/apply_workflow.py" "$@"
