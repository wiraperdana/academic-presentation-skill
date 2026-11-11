# Format outline.md

Outline adalah **satu-satunya sumber kebenaran** deck. Tiga keluaran lain diturunkan darinya oleh script: deck PPTX yang bisa disunting, kumpulan prompt infografis, dan deck gambar. Analoginya seperti naskah film. Kamera, tata cahaya, dan poster semuanya mengacu ke naskah yang sama, jadi yang direvisi cukup naskahnya.

Karena itu formatnya ketat. Script membacanya baris per baris, bukan menebak.

## Frontmatter

Diapit dua baris `---` di awal berkas. Satu field per baris, berbentuk `kunci: nilai`.

| Field | Wajib | Isi |
|---|---|---|
| `judul` | ya | Judul presentasi, dipakai di cover dan footer |
| `judul_singkat` | tidak | Versi pendek untuk footer |
| `subjudul` | tidak | |
| `penyaji` | tidak | Nama, boleh dengan NPM |
| `afiliasi` | tidak | Fakultas, universitas |
| `pembimbing` | tidak | Contoh `Pembimbing: Prof. X` |
| `acara` | tidak | `seminar-proposal`, `seminar-hasil`, `sidang`, `konferensi`, `kuliah`, atau bebas |
| `acara_label` | tidak | Label yang tampil di cover, contoh `SEMINAR HASIL` |
| `tanggal` | tidak | Tulis seperti yang ingin ditampilkan, contoh `Depok, 17 Juli 2026` |
| `durasi_menit` | tidak | Dipakai untuk memeriksa kewajaran jumlah slide |
| `audiens` | tidak | Siapa yang menonton, masuk ke prompt infografis |
| `bahasa` | tidak | `id` (default) atau `en`, bahasa teks di dalam gambar |
| `gaya_visual` | tidak | Gaya bersama semua infografis, dalam bahasa Inggris |
| `ruang_badge` | tidak | `kanan-atas` agar infografis menyisakan pojok kanan atas untuk badge institusi. Tempel badgenya lewat `build_image_deck.py --badge` |
| `galeri_gaya` | tidak | Folder contoh slide infografis yang disukai pengguna, dipakai sebagai rujukan desain per slide |

## Slide

Setiap slide diawali heading level dua dengan ID berurutan:

```markdown
## S03 · Judul slide
```

Pemisah antara ID dan judul boleh `·`, `|`, `:`, atau `-`. ID wajib `S` diikuti dua atau tiga angka.

Di bawah heading, field ditulis sebagai butir `- kunci: nilai`. Field daftar (`isi`, `teks_gambar`) diisi butir yang menjorok dua spasi.

| Field | Wajib | Isi |
|---|---|---|
| `peran` | ya | Fungsi slide. Daftar nilainya di bawah |
| `bagian` | ya | `opening`, `middle`, atau `closing` |
| `pesan` | ya, kecuali `cover` dan `bagian` | **Satu kalimat** yang harus diingat penonton. Di deck PPTX ia tampil sebagai kalimat inti di bawah judul |
| `isi` | tidak | Poin pendek, idealnya 3 sampai 5, masing-masing di bawah 16 kata |
| `visual` | tidak | Arahan gambar: apa yang digambar dan hubungan apa yang harus terlihat |
| `gambar` | tidak | Path gambar asli (relatif terhadap outline), misalnya grafik dari paper. Mengisi kotak visual deck PPTX |
| `data` | tidak | Angka yang harus diplot persis di infografis, contoh `WD 5207; BF 3101; SSO 243` |
| `istilah` | tidak | Daftar `istilah: definisi singkat` untuk strip istilah dasar di infografis |
| `rujukan_gaya` | tidak | Nama berkas di `galeri_gaya` (atau path) yang jadi rujukan desain slide ini. Pilih per slide lewat `katalog-gaya.md` |
| `teks_gambar` | tidak | Menggantikan daftar teks yang diizinkan muncul di infografis. Pakai bila judul dan isi terlalu panjang untuk gambar |
| `sumber` | wajib bila ada angka | Lokasi bukti, contoh `[01, hal. 12]`, atau sitasi APA 7 |
| `catatan` | tidak | Naskah bicara. Masuk ke catatan pembicara di kedua deck |

### Nilai `peran`

`cover`, `gambaran-umum`, `capaian`, `manfaat`, `latar-belakang`, `state-of-the-art`, `masalah`, `tujuan`, `ruang-lingkup`, `kontribusi`, `metode`, `ilustrasi`, `perbandingan`, `eksperimen`, `hasil`, `demo`, `kesimpulan`, `rencana`, `penutup`, `bagian` (pembatas antarbagian), `lainnya`.

Nilai ini adalah label kerja skill, sebagian besar mengikuti judul slide di contoh rujukan. Ia tidak tampil di slide.

## Contoh satu slide

```markdown
## S07 · Hasil utama
- peran: hasil
- bagian: middle
- pesan: Algoritma usulan menekan kerusakan hingga 95% dibanding metode pembanding terlemah.
- isi:
  - Diuji pada 10 skenario serangan
  - Unggul di semua skenario berkerumun
  - Waktu iterasi setara metode pembanding
- visual: diagram batang kerusakan kumulatif empat algoritma, batang usulan paling pendek dan disorot warna aksen
- data: WD 5207; BF 3101; ST 607; Usulan 243
- gambar: sumber/render/01-paper-14.png
- sumber: [01, hal. 14, Tabel 4.3]
- catatan: Tekankan bahwa keunggulan terbesar muncul saat penyerang berkerumun.
```

## Pemeriksaan

```bash
python3 scripts/outline.py check outline.md
```

**GALAT** menghentikan build. **CATAT** adalah saran berdasarkan prinsip di `prinsip-presentasi.md`, dan boleh diabaikan dengan alasan yang jelas.
