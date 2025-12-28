# 🚀 Ultimate Bahasa Lo REPL – Final v5

Ultimate Bahasa Lo REPL adalah REPL berbasis Python untuk coding ringan, fun, dan fleksibel. Cocok untuk Termux/Linux.

---

## ⚡ Fitur Utama

| Fitur | Perintah / Alias | Keterangan |
|-------|----------------|-----------|
| 📝 Bahasa Lo | Echo → tulis<br>If → jika<br>Elif → apabila<br>Then / : → Maka | Alias perintah custom |
| 📂 File Manager | ls, cat <file>, pindah <file> <folder> | List file, baca file, pindah file |
| 📁 Folder Management | cd <folder>, cd .., cd /, keluar_folder | Navigasi folder, prompt otomatis |
| 🔌 Plugin System | plugin, plugin -m | Buat/unggah plugin Python & aktifkan |
| 🌐 Network & Download | ping <host>, curl <url>, wget <url>, git <repo> | Tools jaringan & download ke folder downloads/ |
| 🐧 Proot-Distro | linux | Install & login distro Linux, status installed ditampilkan |
| 💾 Backup & Root Mode | simpan, root -a | Backup data & session, ubah prompt root |
| 🛠 Admin Menu | admin | Tweak repositori & update paket |
| 🔄 Session | otomatis | Variabel & macro tersimpan di .session |
| ⏱ Macros | custom | Shortcut perintah |
| ❓ Bantuan | bantuan | Daftar semua command & fitur |

---

## 📂 Struktur Folder
/REPL bahasa-lo.py      # main script downloads/        # hasil download wget/git/curl plugins/        # plugin Python backup/           # backup session & data .session          # session file
Salin kode

---

## ⚙ Cara Pakai

1. Jalankan REPL:
python3 bahasa-lo.py
Salin kode

2. Prompt REPL muncul:
(+)>   # root REPL
Salin kode

3. Contoh perintah:
tulis "Hello World" cd downloads ls cd .. keluar_folder plugin git https://github.com/user/repo.git simpan root -a
Salin kode

4. Keluar REPL:
keluar
Salin kode

Session akan tersimpan otomatis.

---

## 📌 Catatan

- Semua command Linux (ls, cat, ping, dll) respect folder aktif REPL, tidak tersasar ke `/` sistem  
- Plugin menggunakan Python, bisa buat script custom  
- Folder root REPL selalu `(+) >` atau `[Root]>`  
- CD ke `/` aman → tidak akan ke `/` sistemll
