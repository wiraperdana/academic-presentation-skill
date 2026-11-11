# academic-presentation-skill

Skill agent untuk menyusun presentasi akademik dari bahan apa pun: paper, PDF, slide PPTX lama, DOCX, catatan Markdown, URL, atau kombinasinya. Cocok untuk seminar proposal, seminar hasil, sidang tesis atau disertasi, talk konferensi, dan kuliah.

Satu outline menjadi sumber kebenaran. Dari situ script menurunkan tiga keluaran lain, sehingga revisi cukup dilakukan di outline.

| Keluaran | Isi |
|---|---|
| `outline.md` | Outline slide: pesan inti, poin isi, arahan visual, sumber bukti, naskah bicara |
| `deck.pptx` | Deck yang bisa disunting, dengan catatan pembicara |
| `prompts.md` | Satu prompt slide infografis per slide, siap ditempel ke ChatGPT, Gemini, Canva, atau generator lain |
| `deck-infografis.pptx` | Deck yang tiap slide-nya gambar infografis hasil [claude-imagegen](https://github.com/wiraperdana/claude-imagegen-skill) |

## Prinsip

Laporan ilmiah disusun berurutan, dari latar belakang sampai kesimpulan. Presentasi bekerja terbalik, yaitu **top-down**: gambaran umum dulu, ringkasan hasil di awal, ilustrasi di bagian tengah, dan penutup yang ringkas tanpa nada masalah. Presentasi menyederhanakan isi laporan, bukan menulis ulang laporan.

Prinsip ini dirangkum dari materi *The Art of Academic Presentation* karya Ario Yudo Husodo (Fakultas Ilmu Komputer, Universitas Indonesia). Rinciannya ada di `skills/academic-presentation/references/prinsip-presentasi.md`, dan pemeriksa outline (`outline.py check`) menegakkannya sebagai peringatan.

## Prasyarat

- `python3` dan [`uv`](https://docs.astral.sh/uv/)
- poppler (`pdftotext`, `pdftoppm`) dan LibreOffice (`soffice`)
- Untuk deck infografis: [claude-imagegen-skill](https://github.com/wiraperdana/claude-imagegen-skill) dan Codex CLI yang login dengan akun ChatGPT

## Pasang

```bash
git clone https://github.com/wiraperdana/academic-presentation-skill.git
cd academic-presentation-skill
./install.sh
```

`install.sh` membuat symlink `~/.claude/skills/academic-presentation` dan `~/.agents/skills/academic-presentation`, jadi skill terbaca Claude Code dan Codex.

## Pakai

Di Claude Code: `/academic-presentation buat slide seminar hasil 20 menit dari paper.pdf dan slide-lama.pptx`.

Script juga bisa dijalankan langsung:

```bash
S=skills/academic-presentation/scripts
uv run $S/ingest.py --out presentasi/sumber --render paper.pdf slide-lama.pptx https://contoh.org/artikel
python3 $S/outline.py check presentasi/outline.md
uv run $S/build_pptx.py presentasi/outline.md --out presentasi/deck.pptx
python3 $S/build_prompts.py presentasi/outline.md --out-dir presentasi
$S/gen_images.sh --dir presentasi --only S01            # jangkar gaya, periksa dulu
$S/gen_images.sh --dir presentasi --anchor S01          # sisanya
uv run $S/build_image_deck.py presentasi/outline.md --dir presentasi --out presentasi/deck-infografis.pptx
```

Coba dengan outline contoh di `skills/academic-presentation/examples/contoh-outline.md`. Topik dan angkanya fiktif.

## Perlu diketahui

- Prompt dan gambar rujukan terkirim ke OpenAI lewat Codex. Jangan pakai untuk materi rahasia tanpa izin.
- Setiap gambar memakai kuota langganan ChatGPT, sekitar 2 menit per gambar.
- Teks dan angka di dalam gambar bisa salah. Periksa setiap gambar, dan pakai grafik asli dari paper untuk slide hasil.
- Skill tidak mengarang angka atau sitasi. Setiap angka di outline wajib menunjuk lokasinya di bahan masukan.

## Lisensi

MIT, lihat [LICENSE](LICENSE).
