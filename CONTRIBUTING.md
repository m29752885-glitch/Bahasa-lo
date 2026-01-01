# CONTRIBUTING – Bahasa-lo

Terima kasih sudah mau berkontribusi ke **Bahasa-lo**! 🎉  
Ikuti panduan ini supaya kontribusi kamu lancar.

---

## Cara Mulai

1. Fork repo ini  
2. Clone ke lokal / VPS:  
   git clone https://github.com/m29752885-glitch/Bahasa-lo.git  
3. Masuk folder repo:  
   cd Bahasa-lo  
4. Buat branch baru untuk fitur / bug fix:  
   git checkout -b nama-fitur

---

## Struktur Folder

Bahasa-lo/  
├── main.py  
├── blo_interpreter.py  
├── blo_repl.py  
├── plugin_loader.py  
├── downloads/  
│   ├── plugins/  
│   └── packages/  
├── README.md  
└── config/  
    └── pkg_config.py

- Semua plugin diletakkan di ./downloads/plugins  
- Plugin harus .py dan fungsi utama bisa dipanggil saat di‑load  
- Plugin bisa diaktifkan manual atau auto‑reload

---

## Plugin

Auto reload plugin tertentu:  
from plugin_loader import auto_reload_all  
auto_reload_all()

Aktifkan plugin manual (satu plugin):  
from plugin_loader import activate_single_plugin  
activate_single_plugin("NamaPlugin")

---

## REPL & .blo

- `.blo` → versi Python bahasa Indonesia  
- Jalankan REPL:  
  python blo_repl.py

Contoh perintah di .blo:  
tulis "Halo Dunia"  
masukan "Nama kamu: "

Jalankan file .blo:  
jalankan namafile.blo

---

## Coding Style

- Indentasi 4 spasi  
- Gunakan snake_case untuk variabel/fungsi  
- Tambahkan komentar  
- Jangan hapus fitur lama tanpa izin

---

## Bug & Pull Request

1. Laporkan bug via Issues  
   - Sertakan deskripsi, langkah reproduksi, log/error

2. Commit perubahan:  
   git add .  
   git commit -m "Menambahkan fitur XYZ"

3. Push ke branch:  
   git push origin nama-branch

4. Buat Pull Request ke main

---

## Aturan

- Jangan hapus main.py, blo_interpreter.py  
- Plugin auto hanya untuk plugin aman  
- Gunakan bahasa Indonesia di .blo  
- Semua download masuk ./downloads/packages
