#!/usr/bin/env bash
# Membuat gambar slide infografis dari briefs/*.txt lewat skill claude-imagegen, satu per satu.
# Pakai: gen_images.sh --dir <folder-deck> [--anchor S01 | --ref gaya.png] [--only S03,S05] [--force] [--dry-run]
#
# --anchor S01  gambar slide itu dipakai sebagai rujukan gaya untuk slide lain (disarankan,
#               setelah S01 diperiksa dan disetujui).
# --ref FILE    rujukan gaya dari luar, misalnya template kampus yang sudah dirender.
# --only        hanya slide tertentu, dipisah koma. Berguna untuk revisi.
# --force       timpa gambar yang sudah ada. Tanpa ini, slide yang sudah punya gambar dilewati.
set -euo pipefail

dir=""; anchor=""; ref=""; only=""; force=0; dry=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dir) dir=$2; shift 2 ;;
    --anchor) anchor=$2; shift 2 ;;
    --ref) ref=$2; shift 2 ;;
    --only) only=",$2,"; shift 2 ;;
    --force) force=1; shift ;;
    --dry-run) dry=1; shift ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "Argumen tidak dikenal: $1" >&2; exit 2 ;;
  esac
done
[[ -n "$dir" && -d "$dir/briefs" ]] || { echo "Wajib: --dir berisi folder briefs/ (jalankan build_prompts.py dulu)" >&2; exit 2; }
[[ -z "$ref" || -f "$ref" ]] || { echo "Rujukan tidak ditemukan: $ref" >&2; exit 2; }

gen="${CLAUDE_IMAGEGEN_GEN:-}"
for c in "$gen" "$HOME/.claude/skills/claude-imagegen/scripts/gen.sh" "$HOME/.agents/skills/claude-imagegen/scripts/gen.sh"; do
  if [[ -n "$c" && -x "$c" ]]; then gen=$c; break; fi
done
[[ -n "$gen" && -x "$gen" ]] || {
  echo "gen.sh milik claude-imagegen tidak ditemukan. Pasang https://github.com/wiraperdana/claude-imagegen-skill atau set CLAUDE_IMAGEGEN_GEN." >&2
  exit 3
}

mkdir -p "$dir/images"
made=0; skipped=0; failed=()
for brief in "$dir"/briefs/S*.txt; do
  id=$(basename "$brief" .txt)
  [[ -z "$only" || "$only" == *",$id,"* ]] || continue
  out="$dir/images/$id.png"
  if [[ -f "$out" && $force -eq 0 ]]; then skipped=$((skipped + 1)); continue; fi
  args=(--out "$out" --brief "$brief")
  [[ -n "$ref" ]] && args+=(--ref "$ref")
  if [[ -n "$anchor" && "$id" != "$anchor" && -f "$dir/images/$anchor.png" ]]; then
    args+=(--ref "$dir/images/$anchor.png")
  fi
  [[ $dry -eq 1 ]] && args+=(--dry-run)
  echo "== $id"
  if "$gen" "${args[@]}"; then made=$((made + 1)); else failed+=("$id"); fi
done

[[ $dry -eq 1 ]] && echo "(dry-run, tidak ada gambar yang dibuat)"
echo "Selesai: $made diproses, $skipped dilewati karena sudah ada, ${#failed[@]} gagal ${failed[*]:-}"
[[ ${#failed[@]} -eq 0 ]]
