#!/usr/bin/env bash
# Initialize .ai/ agent development layout in a target repository.
set -euo pipefail

TARGET="${1:-.}"
TARGET="$(cd "$TARGET" && pwd)"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TPL="$SKILL_DIR/templates"

if [[ ! -d "$TPL" ]]; then
  echo "error: templates not found at $TPL" >&2
  exit 1
fi

mkdir -p "$TARGET/.ai/specs"

copy_if_missing() {
  local src="$1" dest="$2"
  if [[ -f "$dest" ]]; then
    echo "skip (exists): $dest"
  else
    cp "$src" "$dest"
    echo "created: $dest"
  fi
}

copy_if_missing "$TPL/root-AGENTS.md" "$TARGET/AGENTS.md"
copy_if_missing "$TPL/ai-AGENTS.md" "$TARGET/.ai/AGENTS.md"
copy_if_missing "$TPL/CONSTITUTION.md" "$TARGET/.ai/CONSTITUTION.md"
copy_if_missing "$TPL/UI-SPEC.md" "$TARGET/.ai/UI-SPEC.md"
copy_if_missing "$TPL/specs-README.md" "$TARGET/.ai/specs/README.md"

TODAY="$(date +%Y-%m-%d)"
EXAMPLE_SPEC="$TARGET/.ai/specs/${TODAY}-example-feature.spec.md"

if [[ ! -f "$EXAMPLE_SPEC" ]]; then
  cp "$TPL/spec.example.md" "$EXAMPLE_SPEC"
  echo "created: $EXAMPLE_SPEC (rename slug in filename after editing)"
else
  echo "skip (exists): $EXAMPLE_SPEC"
fi

echo ""
echo "Done. Next: edit .ai/AGENTS.md, .ai/CONSTITUTION.md, and .ai/UI-SPEC.md for this project."
echo "Spec layout: .ai/specs/YYYY-MM-DD-<slug>.spec.md (§4.8 UI Prompt; see .ai/specs/README.md)"
echo "MasterGo: auxiliary only — distill into spec + UI-SPEC, do not commit raw/screenshots by default."
echo "After migrating legacy docs, run:"
echo "  bash \"$SCRIPT_DIR/cleanup-legacy-docs.sh\" \"$TARGET\""
echo "  bash \"$SCRIPT_DIR/migrate-spec-layout.sh\" \"$TARGET\"   # if flat *.spec.md exist"
