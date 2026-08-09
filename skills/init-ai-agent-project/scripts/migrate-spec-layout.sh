#!/usr/bin/env bash
# Migrate legacy .ai/specs/YYYY-MM-DD-slug/spec.md → flat *.spec.md
# Warn on raw design artifacts that should be distilled into a spec.
set -euo pipefail

TARGET="${1:-.}"
TARGET="$(cd "$TARGET" && pwd)"
SPECS="$TARGET/.ai/specs"

if [[ ! -d "$SPECS" ]]; then
  echo "error: $SPECS not found" >&2
  exit 1
fi

for dir in "$SPECS"/*/; do
  [[ -d "$dir" ]] || continue
  slug_dir="$(basename "$dir")"
  legacy="$dir/spec.md"
  flat="$SPECS/${slug_dir}.spec.md"
  if [[ -f "$legacy" && ! -f "$flat" ]]; then
    git mv "$legacy" "$flat" 2>/dev/null || mv "$legacy" "$flat"
    echo "migrated: $legacy -> $flat"
  fi
  if [[ -d "$dir/mastergo" ]]; then
    echo "warn: $dir/mastergo/ — distill into spec §4.8 then remove (see specs/README.md)"
  fi
  # Remove empty dir if only README left
  if [[ -f "$flat" && -z "$(find "$dir" -mindepth 1 -maxdepth 1 ! -name 'README.md' 2>/dev/null)" ]]; then
    rm -f "$dir/README.md" 2>/dev/null || true
    rmdir "$dir" 2>/dev/null && echo "removed empty: $dir" || true
  fi
done

if [[ -d "$TARGET/.ai/mastergo-output" ]]; then
  echo "warn: .ai/mastergo-output/ — archive or delete; do not use as验收依据"
fi
if [[ -d "$TARGET/.ai/mastergo" ]]; then
  echo "info: .ai/mastergo/ — legacy extracts; distill durable requirements into the relevant spec"
fi

echo ""
echo "migrate-spec-layout done for $TARGET"
