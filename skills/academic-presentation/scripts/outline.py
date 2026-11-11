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
    python3 outline.py tandai outline.md    # kelompokkan field: tampil di gambar atau tidak

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


# Pengelompokan field menurut nasibnya di infografis. Dipakai perintah "tandai".
GROUPS = [
    ("pengaturan slide, tidak tampil", ["peran", "bagian", "rujukan_gaya"]),
    ("TAMPIL DI GAMBAR (judul slide juga tampil)", ["pesan", "istilah", "isi", "data", "teks_gambar"]),
    ("tidak tampil di gambar: arahan visual, jejak bukti, catatan pembicara", ["visual", "gambar", "sumber", "catatan"]),
]
MARK_PREFIX = "<!-- ▸ "


def tandai(path: str | Path) -> int:
    """Susun ulang field tiap slide ke tiga kelompok berpenanda komentar. Isi field tidak diubah."""
    path = Path(path)
    before = parse(path)
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    i = 0
    known = [f for _, fs in GROUPS for f in fs]
    while i < len(lines):
        ln = lines[i]
        if not HEAD_RE.match(ln):
            out.append(ln)
            i += 1
            continue
        out.append(ln)
        i += 1
        chunks: dict[str, list[str]] = {}
        order: list[str] = []
        tail: list[str] = []
        cur = None
        while i < len(lines) and not lines[i].startswith("## "):
            l2 = lines[i]
            fm = FIELD_RE.match(l2)
            if fm:
                cur = fm.group(1)
                chunks[cur] = [l2]
                order.append(cur)
            elif l2.startswith(MARK_PREFIX):
                pass  # penanda lama dibuang, ditulis ulang di bawah
            elif cur and l2.startswith("  "):
                chunks[cur].append(l2)
            elif not l2.strip():
                cur = None
                tail.append(l2)
            else:
                tail.append(l2)
            i += 1
        peran = chunks.get("peran", ["- peran: lainnya"])[0].split(":", 1)[1].strip()
        for label, fields in GROUPS:
            present = [f for f in fields if f in chunks]
            if label.startswith("TAMPIL") and peran == "cover":
                out.append(f"{MARK_PREFIX}TAMPIL DI GAMBAR: judul slide, plus penyaji, afiliasi, acara, dan tanggal dari frontmatter -->")
                for f in present:
                    out.extend(chunks[f])
                continue
            if not present:
                continue
            out.append(f"{MARK_PREFIX}{label} -->")
            for f in present:
                out.extend(chunks[f])
        others = [f for f in order if f not in known]
        for f in others:
            out.extend(chunks[f])
        out.extend(t for t in tail if t.strip()) 
        out.append("")
    text = "\n".join(out).rstrip("\n") + "\n"
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    path.write_text(text, encoding="utf-8")
    after = parse(path)
    same = before[0] == after[0] and [(s.id, s.judul, s.fields) for s in before[1]] == [(s.id, s.judul, s.fields) for s in after[1]]
    print(f"{len(after[1])} slide ditandai. Isi field {'utuh' if same else 'BERUBAH, periksa'}.")
    return 0 if same else 1


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[1] == "tandai":
        return tandai(argv[2])
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
