## CONTRIBUTING – Bahasa-lo
Terima kasih sudah mau berkontribusi ke Bahasa-lo! 🎉
Ikuti panduan singkat ini supaya kontribusi lo lancar.
# Cara Mulai
Fork repo ini
Clone ke lokal / VPS:
``git clone https://github.com/m29752885-glitch/Bahasa-lo.git``
# Masuk folder repo:
``cd Bahasa-lo``
# Buat branch baru untuk fitur / bug fix:
``git checkout -b nama-fitur``
# Struktur Folder
Bahasa-lo/
├── main.py                # Entry point sistem
├── blo_interpreter.py     # Kamus & translator Bahasa-lo
├── blo_repl.py            # REPL Bahasa-lo (.blo)
├── plugin_loader.py       # Loader & manager plugin
├── downloads/
│   ├── plugins/           # Semua plugin (.py)
│   └── packages/          # Hasil download (wget/curl/git)
├── README.md
└── config/
└── pkg_config.py      # Konfigurasi folder & progress
Semua plugin diletakkan di ./downloads/plugins/
Plugin harus .py dan fungsi utama bisa dipanggil saat load
Plugin bisa diaktifkan manual atau auto reload
# Plugin
Auto reload plugin tertentu:
from plugin_loader import auto_reload_all
auto_reload_all()
Aktifkan plugin manual (single plugin):
from plugin_loader import activate_single_plugin
activate_single_plugin("NamaPlugin")
# REPL & .blo
.blo → versi Python bahasa Indonesia
Jalankan REPL:
python blo_repl.py
Contoh perintah di .blo:
tulis "Halo Dunia"
masukan "Nama kamu: "
Jalankan file .blo:
jalankan namafile.blo
Coding Style
Indentasi 4 spasi
Gunakan snake_case untuk variabel/fungsi
Tambahkan komentar
Jangan hapus fitur lama tanpa izin
Bug & Pull Request
Laporkan bug via Issues
Sertakan deskripsi, langkah reproduksi, log/error
# Commit perubahan:
git add .
git commit -m "Menambahkan fitur XYZ"
Push ke branch:
git push origin nama-branch
Buat Pull Request ke main
## Aturan
Jangan hapus: main.py, blo_interpreter.py
Plugin auto hanya untuk plugin aman
Gunakan bahasa Indonesia di .blo
Semua download masuk ./downloads/packages/
