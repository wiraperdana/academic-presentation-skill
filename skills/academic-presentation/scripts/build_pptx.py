# /// script
# requires-python = ">=3.10"
# dependencies = ["python-pptx>=1.0"]
# ///
"""Membangun deck PPTX yang bisa disunting dari outline.md.

Setiap slide berisi teks asli (judul, pesan, poin isi), kotak visual, dan catatan
pembicara. Kotak visual diisi gambar bila field 'gambar' menunjuk berkas yang ada.
Bila tidak, kotak itu berisi arahan visual supaya penyaji tahu apa yang perlu ditempel.

Pakai:
    uv run build_pptx.py outline.md --out deck.pptx
    uv run build_pptx.py outline.md --out deck.pptx --template kampus.pptx
    uv run build_pptx.py outline.md --out deck.pptx --primary 1F3A5F --accent 2A9D8F
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outline import check, parse  # noqa: E402

from pptx import Presentation  # noqa: E402
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN  # noqa: E402
from pptx.util import Emu, Inches, Pt  # noqa: E402

FONT = "Calibri"
TEXT = RGBColor(0x22, 0x22, 0x22)
MUTED = RGBColor(0x6B, 0x72, 0x80)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)


def rgb(hexstr: str) -> RGBColor:
    return RGBColor.from_string(hexstr.lstrip("#").upper())


def blank_layout(prs):
    for lay in prs.slide_layouts:
        if lay.name.lower() in {"blank", "kosong"}:
            return lay
    return prs.slide_layouts[len(prs.slide_layouts) - 1]


def clear_slides(prs):
    lst = prs.slides._sldIdLst  # noqa: SLF001
    for sid in list(lst):
        prs.part.drop_rel(sid.rId)
        lst.remove(sid)


def textbox(slide, x, y, w, h, paras, *, size=18, color=TEXT, bold=False,
            align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, bullet=False, italic=False):
    tb = slide.shapes.add_textbox(Emu(x), Emu(y), Emu(w), Emu(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    if isinstance(paras, str):
        paras = [paras]
    for i, t in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run()
        r.text = f"•  {t}" if bullet else t
        f = r.font
        f.name, f.size, f.bold, f.italic = FONT, Pt(size), bold, italic
        f.color.rgb = color
        if bullet:
            p.space_after = Pt(10)
    return tb


def rect(slide, x, y, w, h, fill=None, line=None, dash=False):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(x), Emu(y), Emu(w), Emu(h))
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(1.25)
        if dash:
            s.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    s.shadow.inherit = False
    return s


def picture_fit(slide, path, x, y, w, h):
    pic = slide.shapes.add_picture(str(path), Emu(x), Emu(y))
    scale = min(w / pic.width, h / pic.height)
    pw, ph = int(pic.width * scale), int(pic.height * scale)
    pic.width, pic.height = pw, ph
    pic.left, pic.top = int(x + (w - pw) / 2), int(y + (h - ph) / 2)
    return pic


def notes(slide, s):
    parts = []
    if s.get("catatan"):
        parts.append(s.get("catatan"))
    if s.get("sumber"):
        parts.append(f"Sumber: {s.get('sumber')}")
    if s.get("visual"):
        parts.append(f"Arahan visual: {s.get('visual')}")
    if parts:
        slide.notes_slide.notes_text_frame.text = "\n\n".join(parts)


def build(outline_path: Path, out: Path, template: Path | None, primary: str, accent: str) -> int:
    meta, slides = parse(outline_path)
    err, warn = check(meta, slides)
    for w in warn:
        print(f"CATAT  {w}")
    if err:
        for e in err:
            print(f"GALAT  {e}")
        return 1

    P, A = rgb(primary), rgb(accent)
    if template:
        prs = Presentation(str(template))
        clear_slides(prs)
    else:
        prs = Presentation()
        prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    W, H = prs.slide_width, prs.slide_height
    mx, base = int(W * 0.055), outline_path.parent
    layout = blank_layout(prs)
    short = meta.get("judul_singkat") or meta.get("judul", "")

    for n, s in enumerate(slides, 1):
        sl = prs.slides.add_slide(layout)
        for ph in list(sl.placeholders):
            ph._element.getparent().remove(ph._element)  # noqa: SLF001

        if s.peran == "cover":
            rect(sl, 0, 0, W, H, fill=P)
            rect(sl, mx, int(H * 0.30), int(W * 0.08), int(H * 0.012), fill=A)
            if meta.get("acara_label") or meta.get("acara"):
                textbox(sl, mx, int(H * 0.16), W - 2 * mx, int(H * 0.1),
                        (meta.get("acara_label") or meta.get("acara")).upper(), size=16, color=WHITE, bold=True)
            textbox(sl, mx, int(H * 0.33), W - 2 * mx, int(H * 0.28), s.judul or meta.get("judul"),
                    size=36, color=WHITE, bold=True, anchor=MSO_ANCHOR.TOP)
            sub = [x for x in [meta.get("subjudul")] if x]
            if sub:
                textbox(sl, mx, int(H * 0.60), W - 2 * mx, int(H * 0.08), sub, size=18, color=WHITE)
            who = [x for x in [meta.get("penyaji"), meta.get("afiliasi"), meta.get("pembimbing"), meta.get("tanggal")] if x]
            textbox(sl, mx, int(H * 0.70), W - 2 * mx, int(H * 0.25), who, size=15, color=WHITE)
            notes(sl, s)
            continue

        if s.peran == "bagian":
            rect(sl, 0, 0, W, H, fill=P)
            textbox(sl, mx, int(H * 0.35), W - 2 * mx, int(H * 0.2), s.judul, size=40, color=WHITE, bold=True)
            if s.get("pesan"):
                textbox(sl, mx, int(H * 0.55), W - 2 * mx, int(H * 0.15), s.get("pesan"), size=20, color=WHITE)
            notes(sl, s)
            continue

        # Slide isi: judul, pesan sebagai kalimat inti, poin di kiri, visual di kanan.
        textbox(sl, mx, int(H * 0.05), W - 2 * mx, int(H * 0.11), s.judul, size=28, color=P, bold=True,
                anchor=MSO_ANCHOR.BOTTOM)
        rect(sl, mx, int(H * 0.165), int(W * 0.06), int(H * 0.008), fill=A)
        textbox(sl, mx, int(H * 0.19), W - 2 * mx, int(H * 0.11), s.get("pesan"), size=19, color=A, bold=True)

        top, bottom = int(H * 0.32), int(H * 0.90)
        img = s.get("gambar")
        img_path = (base / img) if img else None
        has_visual = bool(s.get("visual")) or bool(img)
        isi = s.items()
        if has_visual and isi:
            col_w = int((W - 2 * mx) * 0.46)
            vx, vw = mx + col_w + int(W * 0.03), W - 2 * mx - col_w - int(W * 0.03)
        elif has_visual:
            col_w, vx, vw = 0, mx, W - 2 * mx
        else:
            col_w, vx, vw = W - 2 * mx, 0, 0
        if isi and col_w:
            textbox(sl, mx, top, col_w, bottom - top, isi, size=18, bullet=True)
        if vw:
            if img_path and img_path.exists():
                picture_fit(sl, img_path, vx, top, vw, bottom - top)
            else:
                if img:
                    print(f"CATAT  {s.id}: gambar '{img}' tidak ditemukan, diganti kotak arahan visual")
                rect(sl, vx, top, vw, bottom - top, fill=RGBColor(0xF4, 0xF6, 0xF8), line=MUTED, dash=True)
                textbox(sl, vx + int(W * 0.015), top, vw - int(W * 0.03), bottom - top,
                        f"Visual: {s.get('visual')}", size=13, color=MUTED, italic=True,
                        align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

        textbox(sl, mx, int(H * 0.93), int(W * 0.7), int(H * 0.05), short, size=10, color=MUTED)
        textbox(sl, W - mx - int(W * 0.1), int(H * 0.93), int(W * 0.1), int(H * 0.05), str(n), size=10,
                color=MUTED, align=PP_ALIGN.RIGHT)
        notes(sl, s)

    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out))
    print(f"Tersimpan: {out} ({len(slides)} slide)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("outline", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--template", type=Path, help="PPTX kampus atau lab. Slide lamanya dibuang, ukuran dan master dipakai.")
    ap.add_argument("--primary", default="1F3A5F", help="warna utama heks, default navy")
    ap.add_argument("--accent", default="2A9D8F", help="warna aksen heks, default teal")
    a = ap.parse_args()
    return build(a.outline, a.out, a.template, a.primary, a.accent)


if __name__ == "__main__":
    sys.exit(main())
