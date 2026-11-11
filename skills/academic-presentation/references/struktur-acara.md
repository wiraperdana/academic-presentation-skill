# Struktur slide per jenis acara

Setiap jenis acara punya penonton dan pertanyaan yang berbeda. Kerangka di bawah adalah titik awal, bukan cetakan wajib. Kolom **Peran** adalah nilai field `peran` di outline.

Tiga kerangka pertama diturunkan dari contoh seminar proposal, seminar hasil, dan sidang promosi di materi Ario Yudo Husodo (lihat `prinsip-presentasi.md`). Kerangka konferensi adalah adaptasi skill ini untuk talk berdurasi pendek.

## Seminar proposal (`acara: seminar-proposal`)

Pertanyaan penguji: apakah masalahnya layak, posisinya jelas, dan rencananya masuk akal?

| # | Peran | Bagian | Isi |
|---|---|---|---|
| 1 | `cover` | opening | Judul, penyaji, pembimbing, institusi, tanggal |
| 2 | `gambaran-umum` | opening | Satu visual: topik, pendekatan baru, dan isu terbuka |
| 3 | `state-of-the-art` | opening | Posisi riset terhadap karya terdekat |
| 4 | `latar-belakang` | middle | Mengapa masalah ini penting, dengan bukti |
| 5 | `ilustrasi` | middle | Ilustrasi usulan ide penelitian |
| 6 | `masalah` | middle | Rumusan masalah |
| 7 | `tujuan` | middle | Tujuan penelitian |
| 8 | `capaian` | middle | Publikasi atau kemajuan yang sudah ada |
| 9 | `state-of-the-art` | middle | Tren riset, karakteristik teknologi, penelitian paling terkait |
| 10 | `metode` | middle | Rancangan metode dan eksperimen |
| 11 | `rencana` | closing | Jadwal dan target publikasi |
| 12 | `penutup` | closing | Ringkasan dan kontribusi yang diharapkan |

## Seminar hasil (`acara: seminar-hasil`)

Pertanyaan penguji: apa yang sudah dihasilkan, dan seberapa kuat buktinya?

| # | Peran | Bagian | Isi |
|---|---|---|---|
| 1 | `cover` | opening | |
| 2 | `gambaran-umum` | opening | Visual utuh pekerjaan |
| 3 | `capaian` | opening | Publikasi disertasi atau tesis, langsung di awal |
| 4 | `state-of-the-art` | opening | Posisi terhadap karya terdekat |
| 5 | `latar-belakang` | middle | |
| 6 | `metode` | middle | Deskripsi metode dasar |
| 7..n | `perbandingan` | middle | Konvensional versus usulan, satu komponen per slide |
| n+1 | `eksperimen` | middle | Skenario dan lingkungan eksperimen |
| n+2 | `hasil` | middle | Grafik hasil utama dengan angka dari sumber |
| n+3 | `kesimpulan` | closing | Hasil utama dalam angka, kelebihan, rencana |

## Sidang promosi atau sidang akhir (`acara: sidang`)

Pertanyaan penguji: apakah kontribusinya utuh dan teruji? Deck paling panjang, sering 30 sampai 40 slide.

| Blok | Peran berurutan |
|---|---|
| Opening | `cover`, `gambaran-umum`, `capaian` (publikasi utama), `latar-belakang`, `state-of-the-art` (boleh beberapa slide) |
| Pembingkaian | `masalah` (ringkasan tantangan lalu rumusan), `ruang-lingkup`, `kontribusi`, `capaian` (milestone publikasi) |
| Metode | definisi formal masalah, deskripsi metode dasar, skema modifikasi, ringkasan modifikasi, lalu `perbandingan` per komponen |
| Bukti | `demo` (video atau simulasi), `eksperimen`, `hasil`, ablation study, perbandingan dengan metode lain, ringkasan kinerja |
| Closing | `kesimpulan` dengan angka kinerja, lalu `rencana` |

## Talk konferensi (`acara: konferensi`)

Adaptasi skill ini. Durasi 10 sampai 20 menit, penonton lintas topik, jadi gambaran umum dan satu hasil utama lebih penting dari detail metode.

| # | Peran | Bagian |
|---|---|---|
| 1 | `cover` | opening |
| 2 | `gambaran-umum` | opening |
| 3 | `manfaat` | opening |
| 4 | `masalah` | middle |
| 5 | `metode` atau `ilustrasi` | middle |
| 6 | `hasil` | middle |
| 7 | `kesimpulan` | closing |

## Kuliah, kuliah tamu, atau presentasi tugas (`acara: kuliah`)

Pakai kerangka konferensi, tambahkan `bagian` sebagai pembatas antartopik, dan sisipkan contoh konkret di middle-show.
