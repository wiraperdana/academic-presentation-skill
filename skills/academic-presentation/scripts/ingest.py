# /// script
# requires-python = ">=3.10"
# dependencies = ["python-pptx>=1.0", "python-docx>=1.1"]
# ///
"""Mengubah bahan masukan campuran menjadi teks bernomor lokasi, plus gambar halaman.

Bahan yang diterima: PDF, PPTX, DOCX, Markdown atau teks, gambar, folder berisi
berkas-berkas itu, dan URL. Setiap bahan menjadi satu berkas sumber/NN-nama.md
dengan penanda lokasi seperti [hal. 4] atau [slide 7]. Penanda itu dipakai outline
untuk menunjuk asal setiap angka dan klaim.

Dengan --render, halaman PDF dan slide PPTX juga dirender jadi PNG beresolusi rendah
di sumber/render/, supaya agent bisa melihat gambar, grafik, dan tata letak aslinya.

Pakai:
    uv run ingest.py --out <folder-deck>/sumber paper.pdf slide-lama.pptx catatan.md https://contoh.org/artikel
    uv run ingest.py --out <folder-deck>/sumber --render paper.pdf
"""
from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

IMG = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
TXT = {".md", ".txt", ".markdown", ".tex", ".bib", ".csv"}


def slug(name: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").lower()
    return s[:50] or "sumber"


def run(cmd: list[str]) -> str:
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def from_pdf(p: Path) -> tuple[str, int]:
    if not shutil.which("pdftotext"):
        raise RuntimeError("pdftotext tidak ada. Pasang poppler (brew install poppler)")
    n = int(re.search(r"Pages:\s+(\d+)", run(["pdfinfo", str(p)])).group(1))
    out = []
    for i in range(1, n + 1):
        t = run(["pdftotext", "-layout", "-f", str(i), "-l", str(i), str(p), "-"]).strip()
        out.append(f"\n[hal. {i}]\n{t}")
    return "\n".join(out), n


def from_pptx(p: Path) -> tuple[str, int]:
    from pptx import Presentation

    prs = Presentation(str(p))
    out = []
    for i, sl in enumerate(prs.slides, 1):
        texts = []
        for sh in sl.shapes:
            if sh.has_text_frame and sh.text_frame.text.strip():
                texts.append(sh.text_frame.text.strip())
            if getattr(sh, "has_table", False) and sh.has_table:
                for row in sh.table.rows:
                    texts.append(" | ".join(c.text.strip() for c in row.cells))
        pics = sum(1 for sh in sl.shapes if sh.shape_type == 13)
        body = "\n".join(texts)
        if pics:
            body += f"\n(ada {pics} gambar di slide ini, lihat render)"
        if sl.has_notes_slide and sl.notes_slide.notes_text_frame.text.strip():
            body += f"\nCatatan pembicara: {sl.notes_slide.notes_text_frame.text.strip()}"
        out.append(f"\n[slide {i}]\n{body}")
    return "\n".join(out), len(prs.slides)


def from_docx(p: Path) -> tuple[str, int]:
    import docx

    d = docx.Document(str(p))
    out, para = [], 0
    for blk in d.paragraphs:
        if not blk.text.strip():
            continue
        para += 1
        style = blk.style.name.lower() if blk.style is not None else ""
        prefix = "#" * int(style[-1]) + " " if style.startswith("heading") and style[-1].isdigit() else ""
        out.append(f"[par. {para}] {prefix}{blk.text.strip()}")
    for ti, t in enumerate(d.tables, 1):
        out.append(f"\n[tabel {ti}]")
        out += [" | ".join(c.text.strip() for c in r.cells) for r in t.rows]
    return "\n".join(out), para


def from_url(u: str) -> tuple[str, int]:
    req = urllib.request.Request(u, headers={"User-Agent": "academic-presentation-skill/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310
        ctype = r.headers.get("Content-Type", "")
        data = r.read()
    if "pdf" in ctype or u.lower().endswith(".pdf"):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(data)
        return from_pdf(Path(f.name))
    raw = data.decode("utf-8", errors="replace")
    raw = re.sub(r"(?is)<(script|style|nav|footer|header)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>|</p>|</h\d>|</li>", "\n", raw)
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if len(ln) > 2]
    return "\n".join(f"[par. {i}] {ln}" for i, ln in enumerate(lines, 1)), len(lines)


def render(p: Path, dest: Path, stem: str) -> int:
    dest.mkdir(parents=True, exist_ok=True)
    src = p
    if p.suffix.lower() == ".pptx":
        if not shutil.which("soffice"):
            print(f"CATAT  soffice tidak ada, {p.name} tidak dirender")
            return 0
        tmp = Path(tempfile.mkdtemp())
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(tmp), str(p)],
                       capture_output=True, check=True)
        src = tmp / (p.stem + ".pdf")
    if not shutil.which("pdftoppm"):
        print("CATAT  pdftoppm tidak ada, render dilewati")
        return 0
    subprocess.run(["pdftoppm", "-r", "50", "-png", str(src), str(dest / stem)], check=True)
    return len(list(dest.glob(f"{stem}-*.png")))


def expand(inputs: list[str]) -> list[str]:
    out = []
    for x in inputs:
        p = Path(x)
        if p.is_dir():
            out += [str(f) for f in sorted(p.rglob("*")) if f.is_file() and not f.name.startswith(".")]
        else:
            out.append(x)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--render", action="store_true", help="render halaman PDF dan slide PPTX jadi PNG")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)

    rows = []
    for n, x in enumerate(expand(a.inputs), 1):
        is_url = x.startswith(("http://", "https://"))
        name = x if is_url else Path(x).name
        stem = f"{n:02d}-{slug(Path(name).stem if not is_url else name.split('//', 1)[1])}"
        kind, units, note = "", 0, ""
        try:
            if is_url:
                kind = "url"
                text, units = from_url(x)
            else:
                p = Path(x)
                ext = p.suffix.lower()
                if ext == ".pdf":
                    kind, (text, units) = "pdf", from_pdf(p)
                elif ext == ".pptx":
                    kind, (text, units) = "pptx", from_pptx(p)
                elif ext == ".docx":
                    kind, (text, units) = "docx", from_docx(p)
                elif ext in TXT:
                    kind, text = "teks", p.read_text(encoding="utf-8", errors="replace")
                    units = len(text.splitlines())
                elif ext in IMG:
                    kind, text, units = "gambar", f"(gambar: {p.resolve()}. Buka dan baca secara visual.)", 1
                else:
                    kind, text, note = "lain", "", f"format {ext} belum didukung, baca manual"
                if a.render and ext in {".pdf", ".pptx"}:
                    note = f"{render(p, a.out / 'render', stem)} render"
        except Exception as e:  # noqa: BLE001
            text, note = "", f"GAGAL: {e}"
        if text:
            header = f"# {name}\n\nAsal: {x}\nJenis: {kind}\n"
            (a.out / f"{stem}.md").write_text(header + "\n" + text + "\n", encoding="utf-8")
        rows.append((stem, kind, name, units, len(text), note))
        print(f"{stem:40s} {kind:7s} {units:5d} unit {len(text):8d} huruf {note}")

    inv = ["# Inventaris sumber", "", "| Kode | Jenis | Bahan | Unit | Huruf | Catatan |", "|---|---|---|---|---|---|"]
    inv += [f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} |" for r in rows]
    inv += ["", "Unit berarti halaman untuk PDF, slide untuk PPTX, dan paragraf untuk DOCX atau URL.",
            "Rujuk lokasi bukti di outline sebagai `[01, hal. 4]` atau `[02, slide 7]`."]
    (a.out / "inventaris.md").write_text("\n".join(inv) + "\n", encoding="utf-8")
    print(f"Inventaris: {a.out / 'inventaris.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
