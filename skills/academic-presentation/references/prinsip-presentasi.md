# Prinsip presentasi akademik

Berkas ini adalah dasar keputusan skill saat menyusun outline. Isinya dirangkum dari materi **The Art of Academic Presentation** karya Ario Yudo Husodo (Fakultas Ilmu Komputer, Universitas Indonesia), beserta contoh seminar proposal, seminar hasil, dan sidang promosi doktor yang ia bahas di materi itu. Rangkuman dan contoh operasional di bawah adalah tafsiran skill ini, bukan kutipan.

## Gagasan pokok: logika presentasi berlawanan dengan logika laporan

Laporan ilmiah disusun **berurutan**. Latar belakang dulu, lalu masalah, metode, hasil, dan kesimpulan. Banyak presenter memindahkan urutan itu apa adanya ke slide. Hasilnya runut, tetapi penonton baru tahu inti pekerjaan di menit ke-15.

Presentasi bekerja terbalik. Analoginya seperti peta di pintu masuk mal. Pengunjung melihat denah utuh dulu, baru masuk ke toko yang ia minati. Tanpa denah, ia berjalan dari lorong ke lorong dan cepat lelah.

Dipetakan balik ke presentasi:

| Unsur analogi | Unsur presentasi |
|---|---|
| Denah di pintu masuk | Slide **Gambaran Umum** di awal |
| Toko-toko | Detail latar belakang, metode, dan hasil |
| Pengunjung yang lelah | Penonton yang bosan karena tidak tahu arah |

Prinsip ini disebut **top-down**: mulai dari gambaran besar, lalu turun ke detail. Mengapa penting: penguji dan penonton menilai di menit-menit pertama. Kesan awal menentukan apakah mereka mendengarkan dengan positif atau mencari-cari kelemahan.

Satu kalimat yang merangkum semuanya: **presentasi menyederhanakan penyampaian isi laporan, bukan menulis ulang laporan.**

## Tiga bagian presentasi

Skill ini membagi setiap deck menjadi tiga bagian. Nilainya dipakai di field `bagian` pada outline.

### 1. Opening (`opening`)

1. **Mulai dengan gambaran umum topik.** Satu slide visual yang memuat masalah, pendekatan, dan kebaruan sekaligus.
2. **Hindari membuka dengan latar belakang.** Latar belakang tetap ada, tetapi muncul setelah gambaran umum.
3. **Sampaikan ringkasan kemajuan atau hasil di awal.** Contohnya capaian publikasi atau angka hasil utama. Penonton langsung tahu pekerjaan ini sudah sampai mana.
4. **Sebut manfaatnya bagi penonton** bila memungkinkan. Mengapa mereka perlu peduli.

### 2. Middle-show (`middle`)

1. **Ilustrasi lebih mudah dipahami daripada paparan langsung.** Pakai gambar, video, diagram, atau sorotan kalimat kunci.
2. **Manusia berpikir praktis.** Konsep abstrak lebih cepat tertangkap lewat contoh konkret. Materi Ario memakai soal hitungan sederhana sebagai contoh: penonton lebih cepat menangkap persamaan lewat cerita harga makanan dan minuman daripada lewat simbol.
3. **Bandingkan konvensional dan usulan** secara berdampingan bila kontribusinya berupa modifikasi metode. Pola ini dipakai berulang di contoh seminar hasil dan sidang promosi.
4. **Masalah dan keterbatasan disampaikan di sini,** dengan kalimat optimis, bukan di penutup.

### 3. Closing (`closing`)

1. Ringkas, padat, dan sistematis.
2. Tekankan kembali kelebihan dan kontribusi utama.
3. **Hindari menutup dengan pernyataan bernada masalah.**
4. Sampaikan rencana pengembangan ke depan.

## Waspadai kebosanan penonton

- Kita ahli di topik kita. Itu tidak berarti penonton ingin mendengar semua detailnya.
- Saat menyusun, posisikan diri sebagai penonton. Apa yang mereka **perlu** dan **ingin** dengar?
- Penonton punya latar belakang dan kepentingan yang beragam. Penguji metodologi, pakar domain, dan tamu umum menangkap hal yang berbeda.

## Cara skill menerapkan prinsip ini

| Prinsip | Wujudnya di skill |
|---|---|
| Top-down | `outline.py check` memperingatkan bila tidak ada slide `gambaran-umum` dalam tiga slide pertama setelah cover |
| Jangan buka dengan latar belakang | Peringatan bila slide pertama setelah cover berperan `latar-belakang` |
| Ringkasan hasil di awal | Peran `capaian` tersedia dan disarankan di opening |
| Satu pesan per slide | Field `pesan` wajib, berupa satu kalimat yang harus diingat penonton |
| Sederhanakan, jangan menyalin laporan | Peringatan bila poin isi lebih dari 5 atau satu poin lebih dari 16 kata |
| Ilustrasi di middle-show | Field `visual` berisi arahan gambar, dan menjadi dasar prompt infografis |
| Penutup tanpa nada masalah | Peringatan bila slide kesimpulan memuat kata seperti "masalah" atau "kendala" |

## Catatan kejujuran

Materi rujukan memuat infografis populer yang menyebut manusia "90% makhluk visual". Angka itu beredar luas, tetapi sumber primernya tidak jelas. Skill ini **tidak** memakai angka tersebut sebagai alasan, dan tidak boleh menuliskannya ke slide pengguna. Alasan memakai visual cukup bersandar pada pengalaman praktis di atas: ilustrasi mempercepat pemahaman penonton yang beragam.

Ambang jumlah poin, panjang poin, dan rasio slide per menit di `outline.py` adalah **aturan praktis** skill ini, bukan temuan riset. Ubah sesuai kebiasaan program studi atau venue.
