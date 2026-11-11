#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$repo_dir/skills/academic-presentation"

for target_dir in "$HOME/.claude/skills" "$HOME/.agents/skills"; do
  mkdir -p "$target_dir"
  target="$target_dir/academic-presentation"
  if [[ -e "$target" || -L "$target" ]]; then
    if [[ -L "$target" && "$(readlink "$target")" == "$skill_dir" ]]; then
      printf 'Sudah terpasang: %s\n' "$target"
      continue
    fi
    printf 'Target sudah ada, periksa manual: %s\n' "$target" >&2
    exit 1
  fi
  ln -s "$skill_dir" "$target"
  printf 'Terpasang: %s -> %s\n' "$target" "$skill_dir"
done
