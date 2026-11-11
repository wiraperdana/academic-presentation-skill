#!/usr/bin/env python3
"""Menurunkan prompt slide infografis dari outline.md.

Keluaran:
  prompts.md          kumpulan prompt, satu per slide, siap ditempel ke platform lain
                      (ChatGPT, Gemini, Canva, atau generator gambar lain)
  briefs/S01.txt ...  prompt yang sama per berkas, dipakai gen_images.sh

Prompt ditulis dalam bahasa Inggris karena generator gambar lebih patuh pada instruksi
Inggris. Teks di dalam gambar tetap memakai bahasa deck, dan ditulis persis.
Prompt sengaja berisi konten saja: pesan, isi, arahan visual, dan teks yang diizinkan.
Tata letak diserahkan ke generator.

Pakai:
    python3 build_prompts.py outline.md --out-dir <folder-deck>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outline import check, parse  # noqa: E402

DEFAULT_STYLE = (
    "clean modern academic infographic, flat vector illustration with soft depth, "
    "white or very light background, navy (#1F3A5F) as primary color and teal (#2A9D8F) as accent, "
    "generous whitespace, clear visual hierarchy, sans-serif typography, consistent icon style"
)
LANG = {"id": "Indonesian", "en": "English"}


def q(t: str) -> str:
    return "'" + t.replace("'", "’") + "'"


def allowed_text(meta: dict, s) -> list[str]:
    if s.items("teks_gambar"):
        return s.items("teks_gambar")
    if s.peran == "cover":
        vals = [s.judul or meta.get("judul"), meta.get("subjudul"), meta.get("acara_label"),
                meta.get("penyaji"), meta.get("afiliasi"), meta.get("tanggal")]
        return [v for v in vals if v]
    if s.peran == "bagian":
        return [v for v in [s.judul, s.get("pesan")] if v]
    data = [d.strip() for d in str(s.get("data")).split(";") if d.strip()]
    return [v for v in [s.judul, s.get("pesan"), *s.items(), *data] if v]


def prompt_for(meta: dict, s, style: str) -> str:
    lang = LANG.get(meta.get("bahasa", "id"), meta.get("bahasa", "Indonesian"))
    acara = meta.get("acara_label") or meta.get("acara", "academic presentation")
    out = [
        f"Style: {style}. Landscape 16:9 presentation slide. If a reference image is attached, "
        "match its style, palette, and typography closely so the whole deck looks like one series.",
        "",
        f"Purpose: slide {s.id} of an academic presentation ({acara}) titled {q(meta.get('judul', ''))}.",
    ]
    if meta.get("audiens"):
        out.append(f"Audience: {meta['audiens']}.")
    if s.peran == "cover":
        out.append("This is the title slide. Make the research topic instantly recognizable through one strong visual metaphor.")
    elif s.peran == "bagian":
        out.append("This is a section divider slide. One bold visual, very little text.")
    else:
        out.append(f"Key message the audience must grasp in five seconds: {s.get('pesan')}")
        if s.items():
            out.append("Content to show:")
            out += [f"- {x}" for x in s.items()]
    if s.get("visual"):
        out.append(f"Visual direction: {s.get('visual')}")
    if s.get("data"):
        out.append(f"Data to plot exactly, no other values: {s.get('data')}")
    out += [
        "",
        "Integrity rules: use only the facts, numbers, and names given here. Do not invent data, "
        "chart values, axis numbers, citations, equations, logos, institution names, or people. "
        "Do not draw recognizable faces of real people.",
        "",
        f"Text allowed in the image, exactly as written ({lang}): "
        + ", ".join(q(t) for t in allowed_text(meta, s))
        + ". No other text, no watermark, no logos, no slide number. Spell every word exactly as given.",
    ]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("outline", type=Path)
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args()

    meta, slides = parse(a.outline)
    err, warn = check(meta, slides)
    if err:
        for e in err:
            print(f"GALAT  {e}")
        return 1
    style = meta.get("gaya_visual") or DEFAULT_STYLE
    briefs = a.out_dir / "briefs"
    briefs.mkdir(parents=True, exist_ok=True)

    md = [
        f"# Prompt slide infografis: {meta.get('judul', '')}",
        "",
        f"{len(slides)} prompt, satu per slide, diturunkan dari `{a.outline.name}`. "
        "Setiap prompt berdiri sendiri, jadi bisa ditempel apa adanya ke generator gambar mana pun.",
        "",
        "## Cara pakai",
        "",
        "1. Generate S01 lebih dulu. Periksa ejaan dan gayanya sampai cocok.",
        "2. Lampirkan gambar S01 sebagai rujukan gaya saat meng-generate slide lain, supaya seluruh deck tampak satu seri.",
        "3. Periksa setiap hasil: ejaan setiap teks, angka sama persis dengan prompt, tidak ada teks atau logo tambahan.",
        "4. Bila satu teks salah, minta edit sempit: \"Keep everything, change only the text X to Y.\"",
        "",
        "## Gaya bersama",
        "",
        f"> {style}",
        "",
        "Ganti gaya ini di field `gaya_visual` pada frontmatter outline, lalu jalankan ulang script.",
        "",
    ]
    for s in slides:
        p = prompt_for(meta, s, style)
        (briefs / f"{s.id}.txt").write_text(p + "\n", encoding="utf-8")
        md += [f"## {s.id} · {s.judul}", "", f"Peran: `{s.peran}`. Bagian: `{s.get('bagian')}`.", "",
               "```text", p, "```", ""]
    (a.out_dir / "prompts.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Tersimpan: {a.out_dir / 'prompts.md'} dan {len(slides)} brief di {briefs}")
    for w in warn:
        print(f"CATAT  {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
