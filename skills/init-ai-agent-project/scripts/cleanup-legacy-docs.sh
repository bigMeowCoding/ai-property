#!/usr/bin/env bash
# Remove root-level Agent docs after migration to .ai/ layout.
set -euo pipefail

TARGET="${1:-.}"
TARGET="$(cd "$TARGET" && pwd)"

if [[ ! -f "$TARGET/.ai/AGENTS.md" ]]; then
  echo "error: $TARGET/.ai/AGENTS.md not found — migrate content before cleanup" >&2
  exit 1
fi

if [[ ! -f "$TARGET/AGENTS.md" ]]; then
  echo "error: $TARGET/AGENTS.md (root pointer) not found — create it before cleanup" >&2
  exit 1
fi

remove_if_exists() {
  local path="$1"
  if [[ -f "$path" ]]; then
    rm -f "$path"
    echo "removed: $path"
  fi
}

# constitution.md → .ai/CONSTITUTION.md
if [[ -f "$TARGET/constitution.md" ]]; then
  if [[ ! -f "$TARGET/.ai/CONSTITUTION.md" ]]; then
    echo "error: constitution.md exists but .ai/CONSTITUTION.md missing — migrate first" >&2
    exit 1
  fi
  remove_if_exists "$TARGET/constitution.md"
fi

# agents.md (lowercase legacy) — preserve AGENTS.md when both paths share an inode
if [[ -f "$TARGET/agents.md" ]] && [[ ! "$TARGET/agents.md" -ef "$TARGET/AGENTS.md" ]]; then
  remove_if_exists "$TARGET/agents.md"
fi

# plan.md / memory.md — content should already live under .ai/
for legacy in plan.md memory.md; do
  remove_if_exists "$TARGET/$legacy"
done

# Warn deprecated mastergo-output.
if [[ -d "$TARGET/.ai/mastergo-output" ]]; then
  echo "warn: .ai/mastergo-output/ still present — distill requirements into a spec, then archive or remove raw assets" >&2
fi

# Flatten mistaken .ai/docs or .ai/notes if present
for sub in docs notes; do
  dir="$TARGET/.ai/$sub"
  if [[ -d "$dir" ]]; then
    shopt -s nullglob
    for f in "$dir"/*.md; do
      base="$(basename "$f")"
      dest="$TARGET/.ai/$base"
      if [[ -e "$dest" ]]; then
        echo "skip move (exists): $dest"
      else
        mv "$f" "$dest"
        echo "moved: $f -> $dest"
      fi
    done
    shopt -u nullglob
    rmdir "$dir" 2>/dev/null && echo "removed dir: $dir" || {
      echo "warn: $dir not empty — move remaining files manually" >&2
    }
  fi
done

echo ""
echo "Legacy doc cleanup done for $TARGET"
