#!/usr/bin/env python3
"""Membaca dan memeriksa outline.md milik skill academic-presentation.

Format lengkapnya ada di references/format-outline.md. Ringkasnya:

    ---
    judul: ...
    acara: seminar-hasil
    durasi_menit: 20
    ---

    ## S01 · Judul slide
    - peran: cover
    - bagian: opening
    - pesan: satu kalimat yang harus diingat penonton
    - isi:
      - poin pendek
    - visual: arahan gambar
    - sumber: lokasi bukti
    - catatan: naskah bicara

Pakai:
    python3 outline.py check outline.md     # periksa, keluar 1 bila ada galat
    python3 outline.py json  outline.md     # cetak hasil parse sebagai JSON

Hanya memakai pustaka standar, supaya bisa dipanggil tanpa instalasi.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

HEAD_RE = re.compile(r"^##\s+(S\d{2,3})\s*[·|:\-]\s*(.+?)\s*$")
FIELD_RE = re.compile(r"^-\s+([a-z_]+):\s*(.*)$")
ITEM_RE = re.compile(r"^\s{2,}-\s+(.*)$")
NUM_RE = re.compile(r"\d+(?:[.,]\d+)?\s*%|\b\d{2,}(?:[.,]\d+)?\b")

BAGIAN = {"opening", "middle", "closing"}
PERAN = {
    "cover", "gambaran-umum", "capaian", "manfaat", "latar-belakang",
    "state-of-the-art", "masalah", "tujuan", "ruang-lingkup", "kontribusi",
    "metode", "ilustrasi", "perbandingan", "eksperimen", "hasil", "demo",
    "kesimpulan", "rencana", "penutup", "bagian", "lainnya",
}
LIST_FIELDS = {"isi", "teks_gambar", "istilah"}


@dataclass
class Slide:
    id: str
    judul: str
    fields: dict = field(default_factory=dict)
    line: int = 0

    def get(self, key: str, default=""):
        return self.fields.get(key, default)

    def items(self, key: str = "isi") -> list[str]:
        v = self.fields.get(key, [])
        if isinstance(v, str):
            return [v] if v else []
        return list(v)

    @property
    def peran(self) -> str:
        return str(self.get("peran", "lainnya")).strip().lower()


def _clean(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v


def parse(path: str | Path) -> tuple[dict, list[Slide]]:
    text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()
    meta: dict = {}
    i = 0
    if lines and lines[0].strip() == "---":
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            ln = lines[i]
            if ":" in ln and not ln.lstrip().startswith("#"):
                k, v = ln.split(":", 1)
                meta[k.strip()] = _clean(v)
            i += 1
        i += 1

    slides: list[Slide] = []
    cur: Slide | None = None
    key: str | None = None
    for n in range(i, len(lines)):
        ln = lines[n]
        m = HEAD_RE.match(ln)
        if m:
            cur = Slide(id=m.group(1), judul=m.group(2), line=n + 1)
            slides.append(cur)
            key = None
            continue
        if cur is None or not ln.strip():
            continue
        if ln.startswith("## ") or ln.startswith("# "):
            cur, key = None, None
            continue
        fm = FIELD_RE.match(ln)
        if fm:
            key = fm.group(1)
            val = fm.group(2).strip()
            if key in LIST_FIELDS:
                cur.fields[key] = [val] if val else []
            else:
                cur.fields[key] = val
            continue
        im = ITEM_RE.match(ln)
        if im and key:
            prev = cur.fields.get(key)
            if isinstance(prev, list):
                prev.append(im.group(1).strip())
            else:
                cur.fields[key] = ([prev] if prev else []) + [im.group(1).strip()]
            continue
        if key and ln.startswith("  "):
            prev = cur.fields.get(key)
            if isinstance(prev, list) and prev:
                prev[-1] = f"{prev[-1]} {ln.strip()}"
            else:
                cur.fields[key] = f"{prev or ''} {ln.strip()}".strip()
    return meta, slides


def check(meta: dict, slides: list[Slide]) -> tuple[list[str], list[str]]:
    """Kembalikan (galat, peringatan). Galat menghentikan build, peringatan tidak."""
    err: list[str] = []
    warn: list[str] = []
    if not meta.get("judul"):
        err.append("frontmatter: field 'judul' wajib diisi")
    if not slides:
        err.append("tidak ada slide. Heading slide berbentuk '## S01 · Judul'")
        return err, warn

    seen = set()
    for idx, s in enumerate(slides, 1):
        tag = f"{s.id} (baris {s.line})"
        if s.id in seen:
            err.append(f"{tag}: ID ganda")
        seen.add(s.id)
        if int(s.id[1:]) != idx:
            warn.append(f"{tag}: nomor tidak berurutan, diharapkan S{idx:02d}")
        if s.peran not in PERAN:
            err.append(f"{tag}: peran '{s.peran}' tidak dikenal. Pilihan: {', '.join(sorted(PERAN))}")
        b = str(s.get("bagian")).strip().lower()
        if b not in BAGIAN:
            err.append(f"{tag}: bagian wajib salah satu dari opening, middle, closing")
        if s.peran not in {"cover", "bagian"} and not s.get("pesan"):
            err.append(f"{tag}: 'pesan' wajib. Satu kalimat yang harus diingat penonton")
        isi = s.items()
        if len(isi) > 5:
            warn.append(f"{tag}: {len(isi)} poin isi. Lebih dari 5 poin biasanya tanda slide perlu dipecah")
        for it in isi:
            if len(it.split()) > 16:
                warn.append(f"{tag}: poin terlalu panjang ({len(it.split())} kata): '{it[:50]}...'")
        teks = " ".join([s.get("pesan")] + isi)
        if NUM_RE.search(teks) and not s.get("sumber"):
            warn.append(f"{tag}: ada angka tanpa 'sumber'. Setiap angka harus bisa ditelusuri ke bahan masukan")
        if s.peran in {"kesimpulan", "penutup"} and re.search(r"\b(gagal|masalah|kendala|belum berhasil)\b", teks, re.I):
            warn.append(f"{tag}: penutup memuat kata bernada masalah. Pindahkan ke middle-show dengan kalimat optimis")

    first = [s for s in slides if s.peran != "cover"][:3]
    if first and first[0].peran == "latar-belakang":
        warn.append("opening: slide pertama setelah cover adalah latar belakang. Dahulukan gambaran umum")
    if not any(s.peran == "gambaran-umum" for s in first):
        warn.append("opening: tidak ada slide 'gambaran-umum' dalam tiga slide pertama setelah cover")
    if slides[-1].peran not in {"kesimpulan", "penutup", "rencana"}:
        warn.append(f"closing: slide terakhir ({slides[-1].id}) berperan '{slides[-1].peran}', bukan kesimpulan atau penutup")
    order = {"opening": 0, "middle": 1, "closing": 2}
    last = 0
    for s in slides:
        o = order.get(str(s.get("bagian")).strip().lower(), last)
        if o < last:
            warn.append(f"{s.id}: bagian '{s.get('bagian')}' muncul setelah bagian yang lebih akhir")
        last = max(last, o)

    dur = meta.get("durasi_menit", "")
    if dur.isdigit():
        d = int(dur)
        if len(slides) > d * 1.5:
            warn.append(f"{len(slides)} slide untuk {d} menit. Rata-rata di bawah 40 detik per slide, periksa apakah realistis")
        elif len(slides) < d / 3:
            warn.append(f"{len(slides)} slide untuk {d} menit. Lebih dari 3 menit per slide, periksa apakah ada slide yang terlalu padat")
    return err, warn


def main(argv: list[str]) -> int:
    if len(argv) != 3 or argv[1] not in {"check", "json"}:
        print(__doc__)
        return 2
    meta, slides = parse(argv[2])
    if argv[1] == "json":
        print(json.dumps({"meta": meta, "slides": [s.__dict__ for s in slides]}, ensure_ascii=False, indent=2))
        return 0
    err, warn = check(meta, slides)
    print(f"{len(slides)} slide terbaca dari {argv[2]}")
    for e in err:
        print(f"GALAT  {e}")
    for w in warn:
        print(f"CATAT  {w}")
    if not err and not warn:
        print("Bersih.")
    return 1 if err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
