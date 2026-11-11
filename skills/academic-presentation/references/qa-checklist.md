# Daftar periksa sebelum menyerahkan

## Outline

- [ ] `outline.py check` tanpa GALAT. Setiap CATAT sudah ditindaklanjuti atau punya alasan.
- [ ] Slide kedua atau ketiga adalah gambaran umum, bukan latar belakang.
- [ ] Ringkasan capaian atau hasil muncul di opening.
- [ ] Setiap slide punya satu `pesan`, dan pesan itu bisa dibaca tanpa poin isinya.
- [ ] **Setiap angka, nama metode, dan klaim ditelusuri ke bahan masukan** lewat field `sumber`. Tidak ada angka yang dikarang atau dibulatkan diam-diam.
- [ ] Sitasi yang ditambahkan agent, di luar yang ada di bahan masukan, sudah diverifikasi DOI-nya. Bila belum bisa, tandai `[UNVERIFIED]`.
- [ ] Penutup berisi hasil, kelebihan, dan rencana, tanpa nada masalah.
- [ ] Jumlah slide wajar untuk durasinya.

## Deck PPTX yang bisa disunting

- [ ] Render lewat `soffice --headless --convert-to pdf` lalu `pdftoppm`, dan lihat setiap halaman.
- [ ] Tidak ada teks yang meluap keluar kotak atau tertutup gambar.
- [ ] Kotak visual yang masih kosong memang disengaja, dan arahannya jelas bagi penyaji.
- [ ] Catatan pembicara terisi di slide yang punya `catatan`.

## Infografis hasil generate

- [ ] **Ejaan setiap teks** sama persis dengan prompt. Periksa huruf demi huruf, terutama istilah asing dan nama.
- [ ] **Angka sama persis** dengan field `data` atau `pesan`. Grafik tidak memuat angka sumbu atau nilai karangan.
- [ ] Tidak ada teks tambahan, watermark, logo, atau nomor slide liar.
- [ ] Tidak ada wajah tokoh nyata.
- [ ] Gaya konsisten dengan slide jangkar (S01 atau rujukan gaya).
- [ ] Slide hasil dengan grafik data: bila generator tidak bisa menggambar angka dengan tepat, pakai grafik asli dari paper lewat field `gambar` di deck yang bisa disunting, dan beri tahu pengguna.
- [ ] Logo institusi ditempel terpisah di PowerPoint, bukan digambar generator.

## Penyerahan

- [ ] Laporkan path keempat keluaran.
- [ ] Sebutkan slide yang belum bergambar, revisi yang masih perlu, dan CATAT yang sengaja dibiarkan.
