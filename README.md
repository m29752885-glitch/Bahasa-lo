🚀 Bahasa-lo (.blo)

Bahasa-lo adalah bahasa pemrograman berbasis Python dengan kata kunci Bahasa Indonesia, dirancang agar pemula langsung paham logika coding tanpa ribet bahasa Inggris.

> "Belajar logika dulu, syntax belakangan." — Filosofi Bahasa-lo




---

✨ Fitur Utama

🇮🇩 Keyword Bahasa Indonesia (tulis, jika, fungsi, dll)

🧠 Interpreter .blo (translate ke Python otomatis)

💬 REPL interaktif khusus Bahasa-lo

🐧 Command Linux terintegrasi (cd, ls, nano, dll)

🐧 Integrasi proot-distro lewat command linux

🔌 Sistem Plugin modular

📁 Manajemen file & folder (buat, hapus, edit)

🛡️ Permission Engine (user / root / admin)

📦 Auto-manage folder downloads & plugins



---

📂 Struktur Folder

.
bahasa-lo/
├── main.py                  # Entry point sistem
├── blo_interpreter.py       # Kamus & translator Bahasa-lo (.blo → Python)
├── blo_repl.py              # REPL Bahasa-lo
├── plugin_loader.py         # Loader & manager plugin
├── downloads/               # Semua file hasil download & plugin
│   ├── plugins/             # Semua plugin (.py)
│   └── packages/            # Hasil download (wget/curl/git)
├── internal/                # Module internal sistem
│   ├── int_mod_loader.py    # Loader modul internal (backend)
│   └── int_mod/             # Modul internal (seperti permission engine)
│       └── permission_engine.py
└── README.md

---

▶️ Cara Menjalankan

Jalankan sistem utama

python main.py

Masuk REPL Bahasa-lo

jalankan repl

Jalankan file .blo

jalankan namafile.blo


---

🧠 Contoh Kode Bahasa-lo

fungsi sapa(nama):
    jika nama == "admin":
        tulis "Halo Admin"
    lainnya:
        tulis "Halo", nama

sapa("user")


---

🧩 Kamus Bahasa (v1)

Contoh keyword:

Bahasa-lo	Python

tulis	print
masukan	input
jika	if
lainnya	else
fungsi	def
kembalikan	return
Benar	True
Salah	False


(Lengkap ada di blo_interpreter.py)


---

🔌 Sistem Plugin

Auto-load plugin

Plugin berikut auto-load jika ada:

Explorer_fix

Optimasi

crash_handle


Command plugin

plugin -l        # list plugin
plugin -i nama   # aktifkan plugin

Folder plugin:

./downloads/plugins


---

🐧 Command Linux

Bahasa-lo mendukung command Linux langsung:

ls, cd, pwd

nano, cat, rm, mkdir, touch

wget, curl, git clone


📦 Semua hasil download otomatis masuk ke:

./downloads/packages


---

🐧 Masuk proot-distro

linux

Syarat:

Level root atau admin


Flow:

1. Tampilkan distro tersedia


2. Pilih distro ter-install


3. Login ke distro




---

👤 Level Permission

Level	Prompt	Akses

user	(+)>	basic
root	[#]>	linux + system
admin	{+}>	full



---

📘 Plugin Manual

Bahasa-lo mendukung plugin manual interaktif yang menjelaskan semua fitur sistem secara detail.

Aktifkan:

plugin -i manual


---

🎯 Tujuan Proyek

Membantu pemula belajar logika pemrograman

Alternatif Python untuk edukasi lokal

Bisa dipakai di Termux / Linux / VPS



---

📌 Status Proyek

Versi: v1 (stabil)

Target: Open Source

Lisensi: CC-BY / MIT (opsional)



---

🤝 Kontribusi

Pull request & ide sangat diterima 🙌


---

🔥 Bahasa-lo — Ngoding pakai Bahasa Indonesia, otak langsung nyala.
