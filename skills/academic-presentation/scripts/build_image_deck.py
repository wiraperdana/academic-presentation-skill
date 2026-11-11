# /// script
# requires-python = ">=3.10"
# dependencies = ["python-pptx>=1.0"]
# ///
"""Merakit deck PPTX yang tiap slide-nya satu gambar infografis.

Gambar dicari di <folder-deck>/images/<ID>.png (atau .jpg). Catatan pembicara diambil
dari outline, jadi deck gambar tetap bisa dipresentasikan dengan naskah.
Slide yang gambarnya belum ada diberi penanda, bukan dilewati, supaya urutan tetap utuh.

Generator gambar sering menghasilkan rasio 3:2, bukan 16:9. Mode 'contain' (default)
menaruh gambar utuh dan mengisi sisa bidang dengan warna tepi gambar.
Mode 'cover' memotong gambar supaya penuh. Mode 'auto' menyamakan ukuran slide
dengan rasio gambar pertama.

Pakai:
    uv run build_image_deck.py outline.md --dir <folder-deck> --out deck-infografis.pptx [--fit contain|cover|auto]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outline import parse  # noqa: E402

from PIL import Image  # noqa: E402  (ikut terpasang bersama python-pptx)
from pptx import Presentation  # noqa: E402
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN  # noqa: E402
from pptx.util import Emu, Inches, Pt  # noqa: E402


def find_image(d: Path, sid: str) -> Path | None:
    for ext in (".png", ".jpg", ".jpeg"):
        p = d / f"{sid}{ext}"
        if p.exists():
            return p
    return None


def edge_color(path: Path) -> RGBColor:
    im = Image.open(path).convert("RGB")
    w, h = im.size
    pts = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1)]
    px = [im.getpixel(p) for p in pts]
    r, g, b = (sum(c[i] for c in px) // len(px) for i in range(3))
    return RGBColor(r, g, b)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("outline", type=Path)
    ap.add_argument("--dir", type=Path, required=True, help="folder deck berisi images/")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--fit", choices=["contain", "cover", "auto"], default="contain")
    a = ap.parse_args()

    meta, slides = parse(a.outline)
    imgdir = a.dir / "images"
    imgs = {s.id: find_image(imgdir, s.id) for s in slides}

    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    first = next((p for p in imgs.values() if p), None)
    if a.fit == "auto" and first:
        w, h = Image.open(first).size
        prs.slide_height = int(prs.slide_width * h / w)
    W, H = prs.slide_width, prs.slide_height
    layout = prs.slide_layouts[6]
    missing = []

    for s in slides:
        sl = prs.slides.add_slide(layout)
        p = imgs[s.id]
        if p is None:
            missing.append(s.id)
            tb = sl.shapes.add_textbox(0, 0, W, H)
            tf = tb.text_frame
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            for k, line in enumerate([f"{s.id} · {s.judul}", "(gambar belum dibuat)"]):
                para = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
                para.alignment = PP_ALIGN.CENTER
                r = para.add_run()
                r.text = line
                r.font.size, r.font.color.rgb = Pt(28 if k == 0 else 18), RGBColor(0x9C, 0xA3, 0xAF)
        else:
            iw, ih = Image.open(p).size
            if a.fit == "cover":
                scale = max(W / iw, H / ih)
            else:
                scale = min(W / iw, H / ih)
                bg = sl.background.fill
                bg.solid()
                bg.fore_color.rgb = edge_color(p)
            pw, ph = int(iw * scale), int(ih * scale)
            pic = sl.shapes.add_picture(str(p), Emu((W - pw) // 2), Emu((H - ph) // 2), Emu(pw), Emu(ph))
            if a.fit == "cover":
                # Potong bagian yang keluar bidang slide, supaya berkas tidak menyimpan area tersembunyi.
                cx = max(0, (pw - W) / 2 / pw)
                cy = max(0, (ph - H) / 2 / ph)
                pic.crop_left = pic.crop_right = cx
                pic.crop_top = pic.crop_bottom = cy
                pic.left, pic.top, pic.width, pic.height = 0, 0, W, H
        parts = [x for x in [s.get("catatan"), f"Sumber: {s.get('sumber')}" if s.get("sumber") else ""] if x]
        if parts:
            sl.notes_slide.notes_text_frame.text = "\n\n".join(parts)

    a.out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(a.out))
    print(f"Tersimpan: {a.out} ({len(slides)} slide, {len(slides) - len(missing)} bergambar)")
    if missing:
        print(f"CATAT  gambar belum ada untuk: {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
