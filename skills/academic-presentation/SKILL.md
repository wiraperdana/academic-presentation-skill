---
name: academic-presentation
description: Susun presentasi akademik (seminar proposal, seminar hasil, sidang tesis atau disertasi, talk konferensi, kuliah) dari bahan apa pun, yaitu paper, PDF, slide PPTX lama, DOCX, catatan, URL, atau kombinasinya. Menghasilkan empat keluaran dari satu outline, yaitu outline slide Markdown, deck PPTX yang bisa disunting, kumpulan prompt slide infografis untuk platform lain, dan deck PPTX yang tiap slide-nya gambar infografis hasil /claude-imagegen. Prinsipnya top-down, yaitu gambaran umum dulu, ringkasan hasil di awal, ilustrasi di tengah, dan penutup tanpa nada masalah. Pakai saat pengguna meminta "buat slide sidang", "presentasi seminar hasil", "deck dari paper ini", "/academic-presentation", atau ingin paper diubah jadi presentasi.
---

# academic-presentation

Skill ini mengubah bahan riset menjadi presentasi akademik. Satu outline menjadi sumber kebenaran, lalu tiga keluaran lain diturunkan darinya oleh script.

Analoginya seperti naskah film. Sutradara menulis naskah sekali. Tim kamera, tim poster, dan tim trailer semuanya bekerja dari naskah yang sama. Bila ada adegan yang berubah, yang direvisi naskahnya, lalu semua turunan dibuat ulang. Di sini naskahnya `outline.md`, dan turunannya deck PPTX, prompt infografis, serta deck gambar.

## Empat keluaran

| # | Berkas | Isi | Dibuat oleh |
|---|---|---|---|
| 1 | `outline.md` | Outline slide: pesan, isi, arahan visual, sumber, naskah bicara | Agent, disetujui pengguna |
| 2 | `deck.pptx` | Deck yang bisa disunting, teks asli plus kotak visual dan catatan pembicara | `scripts/build_pptx.py` |
| 3 | `prompts.md` | Satu prompt infografis per slide, siap ditempel ke ChatGPT, Gemini, Canva, dan sejenisnya | `scripts/build_prompts.py` |
| 4 | `deck-infografis.pptx` | Deck yang tiap slide-nya satu gambar infografis | `scripts/gen_images.sh` lalu `scripts/build_image_deck.py` |

Semuanya disimpan di satu **folder deck**. Defaultnya `./presentasi-<slug-judul>/`, kecuali pengguna atau aturan workspace menentukan tempat lain.

```
presentasi-<slug>/
  sumber/              teks bahan bernomor lokasi, inventaris.md, render/
  outline.md
  deck.pptx
  prompts.md
  briefs/S01.txt ...   prompt per slide untuk gen_images.sh
  images/S01.png ...
  deck-infografis.pptx
```

## Prasyarat

- `python3` dan [`uv`](https://docs.astral.sh/uv/). Script ber-dependensi dijalankan dengan `uv run`, yang memasang `python-pptx` sendiri di lingkungan sementara.
- `pdftotext`, `pdfinfo`, `pdftoppm` dari poppler, untuk membaca dan merender PDF.
- `soffice` (LibreOffice), untuk merender PPTX saat pemeriksaan visual.
- Untuk keluaran 4: skill [`claude-imagegen`](https://github.com/wiraperdana/claude-imagegen-skill) terpasang, dan Codex CLI sudah login.

Bila salah satu tidak ada, sebutkan yang kurang, lalu kerjakan keluaran yang tetap bisa dibuat.

## Baca dulu

1. `references/prinsip-presentasi.md`: prinsip top-down, opening, middle-show, dan closing. Ini dasar setiap keputusan struktur.
2. `references/struktur-acara.md`: kerangka slide per jenis acara.
3. `references/format-outline.md`: format outline yang dibaca script.

## Prosedur

### Langkah 1. Pahami permintaan

Tanyakan hanya yang belum jelas. Lima hal yang menentukan:

1. **Jenis acara**, misalnya seminar proposal, seminar hasil, sidang, konferensi, atau kuliah.
2. **Durasi** dalam menit.
3. **Penonton**, misalnya penguji, pembimbing, peserta konferensi lintas bidang, atau mahasiswa.
4. **Bahasa** slide.
5. **Keluaran** yang diminta. Default keempatnya. Keluaran 4 memakai kuota imagegen, jadi konfirmasi dulu sebelum langkah 6.

Tanyakan juga data cover yang tidak ada di bahan: nama penyaji, NPM, pembimbing, tanggal, dan tempat.

### Langkah 2. Kumpulkan bahan

```bash
uv run scripts/ingest.py --out <folder-deck>/sumber --render <berkas atau folder>... [url]...
```

Script mengubah setiap bahan jadi `sumber/NN-nama.md` dengan penanda lokasi `[hal. N]`, `[slide N]`, atau `[par. N]`, lalu menulis `sumber/inventaris.md`. Opsi `--render` membuat PNG halaman PDF dan slide PPTX di `sumber/render/`.

- **Baca teksnya utuh,** bukan hanya abstrak. Angka hasil biasanya ada di tabel dan bagian eksperimen.
- **Lihat render-nya** untuk halaman yang memuat grafik, tabel, atau diagram. Teks hasil ekstraksi tidak menangkap isi gambar.
- **URL** diambil sebagai teks HTML sederhana. Bila hasilnya kosong atau berantakan, baca halamannya dengan alat web milik agent, lalu simpan teksnya sebagai berkas `.md` di `sumber/`.
- **Slide PPTX lama** dibaca sebagai bahan, bukan cetakan. Strukturnya tetap disusun ulang menurut prinsip top-down.

### Langkah 3. Susun peta isi

Sebelum menulis slide, tulis ringkasan kerja untuk diri sendiri, tidak perlu disimpan:

- Satu kalimat inti seluruh pekerjaan. Ini calon `pesan` slide gambaran umum.
- Masalah, pendekatan, dan kebaruan.
- Hasil utama dalam angka, **masing-masing dengan lokasi bukti**.
- Kontribusi dan capaian, misalnya publikasi.
- Apa yang **perlu** dan **ingin** didengar penonton ini, dan apa yang boleh dibuang.

### Langkah 4. Sajikan tabel alur dulu, lalu tunggu

Sebelum menulis outline, sajikan **tabel alur**: satu baris per slide, berisi nomor, judul, dan satu kalimat pesan. Tidak ada poin isi, visual, atau sumber di tahap ini.

```
| # | Slide | Pesan (satu kalimat) |
|---|---|---|
| S02 | Gambaran Umum | ... |
```

Aturannya:

1. **Susun dari nol menurut logika penonton,** bukan dengan menambal outline atau dokumen lama. Bahan lama adalah sumber isi, bukan cetakan urutan.
2. **Uji tiap baris:** apakah orang awam bisa mengikuti dari baris sebelumnya ke baris ini tanpa lompatan?
3. **Balasan ringkas.** Tabel alur adalah isi utama balasan. Penjelasan cukup beberapa baris di bawahnya. Pengguna harus bisa menilai alur dalam satu layar.
4. **Tunggu persetujuan atau koreksi** sebelum menulis outline, membangun deck, atau membuat gambar. Koreksi alur di tahap ini paling murah.

Periksa tabel alur terhadap daftar ini:

- Cover hanya judul dan identitas, tanpa subtitle gimmick.
- Gambaran umum memakai kegiatan sehari-hari yang sangat lazim, sehingga penonton ikut merasakan masalahnya.
- Istilah dasar dijelaskan sebelum masuk teknis.
- Latar belakang menunjukkan kegawatan dengan bukti yang berdampak luas: skala pemakaian, kegagalan model terbaik, insiden nyata, dan pengakuan pihak terdepan di bidangnya. Angka yang lemah atau sempit tidak dipakai.
- **Setiap pilihan metode utama punya slide justifikasi:** kenapa pendekatan ini, dibanding alternatifnya, lengkap dengan keterbatasannya.
- Alur penelitian keseluruhan tampil sebagai diagram tahapan. Label luaran, misalnya Paper 1, cukup label kecil, bukan judul besar.
- Label teknis rancangan, misalnya nama peran agen, selalu didahului bahasa manusia.
- Cakupan mengikuti arahan pemilik riset. Bagian di luar cakupan cukup tampil sebagai roadmap.

### Langkah 5. Tulis outline

Salin `templates/outline-template.md` ke `<folder-deck>/outline.md`, lalu isi mengikuti kerangka acara di `references/struktur-acara.md`.

Aturan menulis:

1. **Gambaran umum di slide 2,** bukan latar belakang.
2. **Ringkasan capaian atau hasil di opening.**
3. **Satu pesan per slide.** Field `pesan` berupa kalimat lengkap yang menyatakan temuan atau klaim, bukan label topik. "Okupansi naik dari 58% ke 81%" lebih kuat dari "Hasil eksperimen".
4. **Sederhanakan.** Paling banyak 5 poin isi, masing-masing di bawah 16 kata. Sisanya pindah ke `catatan`.
5. **Ilustrasi di middle-show.** Isi `visual` dengan arahan konkret: apa yang digambar, dan hubungan apa yang harus terlihat.
6. **Perbandingan konvensional dan usulan** berdampingan bila kontribusinya modifikasi metode.
7. **Penutup** berisi hasil utama, kelebihan, dan rencana. Keterbatasan disampaikan di middle-show dengan kalimat optimis.
8. **Integritas bukti.** Setiap angka, nama metode, dan klaim wajib ditelusuri ke bahan lewat field `sumber`. Jangan menambah angka, membulatkan diam-diam, atau mengarang sitasi. Sitasi baru di luar bahan masukan wajib diverifikasi DOI-nya, dan bila tidak bisa, tandai `[UNVERIFIED]`.
9. **Grafik asli.** Bila paper punya grafik hasil, rujuk render halamannya atau potongan gambarnya lewat field `gambar`, supaya deck yang bisa disunting memakai grafik asli.

Lalu tandai apa yang tampil di gambar, supaya pengguna tahu persis teks mana yang akan muncul di slide saat menyunting:

```bash
python3 scripts/outline.py tandai <folder-deck>/outline.md
```

Lalu periksa:

```bash
python3 scripts/outline.py check <folder-deck>/outline.md
```

Perbaiki semua GALAT. Tindak lanjuti setiap CATAT, atau catat alasan mengabaikannya.

**Tunjukkan outline ke pengguna dan tunggu persetujuan** sebelum lanjut. Mengubah outline jauh lebih murah daripada mengubah 30 gambar.

### Langkah 6. Bangun deck PPTX dan prompt

```bash
uv run scripts/build_pptx.py <folder-deck>/outline.md --out <folder-deck>/deck.pptx [--template kampus.pptx] [--primary 1F3A5F --accent 2A9D8F]
python3 scripts/build_prompts.py <folder-deck>/outline.md --out-dir <folder-deck>
```

- `--template` memakai ukuran dan master PPTX kampus atau lab. Slide lamanya dibuang.
- Prompt sengaja berisi **konten saja**: pesan, isi, arahan visual, data, dan daftar teks yang boleh muncul. Tata letak diserahkan ke generator gambar.
- Ganti gaya bersama lewat field `gaya_visual` di frontmatter outline.

### Langkah 7. Generate infografis lewat claude-imagegen

**Pilih rujukan desain per slide bila pengguna punya galeri.** Galeri adalah folder berisi contoh slide infografis yang disukai pengguna. Satu rujukan untuk seluruh deck membuat semua slide bertata letak sama, padahal slide statistik, alur proses, perbandingan, dan istilah butuh layout berbeda.

1. Isi `galeri_gaya: <folder>` di frontmatter outline.
2. Buat lembar kontak galeri, lihat setiap gambar, lalu tulis `<folder-deck>/katalog-gaya.md` memakai format `references/katalog-gaya.md`: satu baris per gambar, berisi pola layout dan peran slide yang cocok.
3. Untuk tiap slide, pilih satu gambar yang pola layout-nya paling cocok dengan peran dan isi slide, lalu isi field `rujukan_gaya: <nama berkas>`. Jangan memakai satu rujukan untuk semua slide, kecuali galerinya memang hanya satu pola.
4. Tunjukkan pemetaan slide ke rujukan sebagai tabel ringkas, lalu tunggu persetujuan pengguna.
5. `build_prompts.py` menulis `briefs/<ID>.ref`, dan `gen_images.sh` melampirkannya otomatis. Prompt sudah memuat larangan menyalin kata, topik, angka, logo, dan sitasi dari rujukan.

Bila galeri berasal dari pekerjaan klien, pakai sebagai rujukan desain saja, dan periksa hasilnya untuk memastikan tidak ada isi klien yang ikut terbawa.


Sampaikan dua hal ini sekali per sesi sebelum mulai:

- Prompt dan gambar rujukan terkirim ke OpenAI lewat Codex. Jangan lanjut untuk materi rahasia atau belum terbit tanpa izin eksplisit pengguna.
- Setiap gambar memakai kuota langganan ChatGPT, sekitar 2 menit per gambar. Deck 30 slide berarti sekitar satu jam.

Lalu jalankan bertahap:

```bash
scripts/gen_images.sh --dir <folder-deck> --only S01 --style-guide <AGENTS.md>   # jangkar gaya
# periksa images/S01.png secara visual, revisi sampai disetujui
scripts/gen_images.sh --dir <folder-deck> --anchor S01          # sisanya, memakai S01 sebagai rujukan gaya
scripts/gen_images.sh --dir <folder-deck> --only S07 --anchor S01 --force   # revisi satu slide
```

Secara default Codex me-refine brief lebih dulu sebagai art director. Bila workspace punya aturan bahasa dan pedagogi, misalnya `AGENTS.md`, teruskan lewat `--style-guide`. Teks di gambar sebaiknya label pendek lewat field `teks_gambar`, karena brief yang padat teks menghasilkan desain yang sesak.

Script mencari `gen.sh` milik claude-imagegen di `~/.claude/skills/` atau `~/.agents/skills/`, atau di variabel `CLAUDE_IMAGEGEN_GEN`. Pakai `--dry-run` untuk melihat perintahnya tanpa memakai kuota. Bila agent yang berjalan adalah Codex sendiri, pakai alat `image_gen` bawaannya per berkas di `briefs/`.

**Periksa setiap gambar secara visual** memakai `references/qa-checklist.md`. Yang paling sering salah: ejaan, angka pada grafik, dan teks liar. Untuk perbaikan kecil, revisi sempit lebih andal daripada generate ulang. Lihat bagian revisi di skill claude-imagegen.

### Langkah 8. Rakit deck gambar

```bash
uv run scripts/build_image_deck.py <folder-deck>/outline.md --dir <folder-deck> --out <folder-deck>/deck-infografis.pptx [--fit contain|cover|auto]
```

Bila slide perlu badge institusi, isi `ruang_badge: kanan-atas` di frontmatter sebelum generate, lalu rakit dengan `--badge <logo.png>`. Logo tidak pernah digambar generator. Slide yang gambarnya bukan hasil generate, misalnya potongan infografis asli, dikecualikan lewat `--badge-skip`.

Generator sering menghasilkan rasio 3:2. `contain` (default) menaruh gambar utuh dengan warna tepi sebagai latar, `cover` memotong supaya penuh, dan `auto` menyamakan ukuran slide dengan gambar. Slide yang gambarnya belum ada diberi penanda, bukan dilewati.

### Langkah 9. Periksa dan serahkan

Render kedua deck dan lihat setiap halaman:

```bash
soffice --headless --convert-to pdf --outdir <folder-deck>/_cek <folder-deck>/deck.pptx <folder-deck>/deck-infografis.pptx
pdftoppm -r 50 -png <folder-deck>/_cek/deck.pdf <folder-deck>/_cek/deck
```

Jalankan `references/qa-checklist.md`. Laporkan ke pengguna:

- Path keempat keluaran.
- Slide yang belum bergambar atau masih perlu revisi.
- CATAT dari `outline.py check` yang sengaja dibiarkan, beserta alasannya.
- Kotak visual di `deck.pptx` yang masih menunggu gambar asli dari pengguna.

## Batasan yang perlu jujur disampaikan

- Generator gambar tidak deterministik, dan teks panjang di dalam gambar sering salah eja. Deck gambar cocok untuk tampilan, sedangkan deck yang bisa disunting tetap jadi pegangan untuk revisi.
- Grafik data hasil generate berisiko memuat angka yang keliru. Untuk slide hasil, grafik asli dari paper lebih aman.
- Logo institusi tidak digambar generator. Tempel sebagai gambar terpisah di PowerPoint.
- Ambang di `outline.py` adalah aturan praktis, bukan temuan riset.
