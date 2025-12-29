#!/usr/bin/env python3
# main.py - Ultimate Bahasa Lo REPL Final

import os, sys, pickle, subprocess, time, re
from config.pkg_config import DOWNLOADS_FOLDER, PACKAGES_FOLDER, ADMIN_FOLDER, BACKUP_FOLDER, progress_bar, LOADING_MSGS, PROGRESS_SPEED

# ----------------------------
# Global
# ----------------------------
variabel = {}
macros = {}
level_akses = "user"  # user, root, admin
prompt_str = "(+)> "
current_folder = "."

PLUGINS_FOLDER = os.path.join(DOWNLOADS_FOLDER, "plugins")
os.makedirs(PLUGINS_FOLDER, exist_ok=True)

# ----------------------------
# Load session
# ----------------------------
session_file = ".session"
if os.path.exists(session_file):
    try:
        with open(session_file,"rb") as f:
            data = pickle.load(f)
            variabel.update(data.get("variabel",{}))
            macros.update(data.get("macros",{}))
        print("Session sebelumnya berhasil dimuat.")
    except:
        print("Gagal load session, lanjut.")

# ----------------------------
# Plugin system (auto reload beberapa plugin)
# ----------------------------
AUTO_RELOAD_PLUGINS = ["Explorer_fix.py","Optimasi.py","crash_handle.py"]
plugins_status = {}
for plugin in os.listdir(PLUGINS_FOLDER):
    plugins_status[plugin] = False

def reload_plugins():
    for plugin in AUTO_RELOAD_PLUGINS:
        path = os.path.join(PLUGINS_FOLDER, plugin)
        if os.path.exists(path):
            try:
                exec(open(path).read(), globals())
                plugins_status[plugin] = True
            except:
                plugins_status[plugin] = False

reload_plugins()

# ----------------------------
# Log
# ----------------------------
log_file = "repl.log"
def log(cmd, output=""):
    with open(log_file,"a") as f:
        f.write(f"CMD> {cmd}\n{output}\n")

# ----------------------------
# Evaluasi ekspresi (Python Indonesia support)
# ----------------------------
def evaluasi_ekspresi(expr):
    # ganti variabel
    for var in variabel:
        expr = re.sub(r'\b'+var+r'\b', str(variabel[var]), expr)
    try:
        return eval(expr)
    except:
        return expr.strip('"')

# ----------------------------
# File Explorer Linux
# ----------------------------
def list_files(folder=None):
    folder = folder or current_folder
    if not os.path.exists(folder):
        print(f"Folder '{folder}' tidak ada!")
        return
    entries = os.listdir(folder)
    for entry in entries:
        path = os.path.join(folder, entry)
        stat = os.stat(path)
        size = stat.st_size
        mtime_str = time.strftime("%b %d %H:%M", time.localtime(stat.st_mtime))
        if os.path.isdir(path):
            print(f"drwxr-xr-x       {mtime_str} {entry}")
        else:
            size_str = f"{size/1024:.1f}K" if size >= 1024 else f"{size}B"
            print(f"-rw-r--r-- {size_str:>6} {mtime_str} {entry}")

# ----------------------------
# Proses perintah
# ----------------------------
def proses_baris(b):
    global prompt_str, current_folder, level_akses

    b = b.strip()
    if b == "" or b.startswith("#"): return None

    # Admin mode
    if b.lower() == "admin":
        pwd = input("Masukkan password admin: ").strip()
        if pwd == "12345":
            level_akses = "admin"
            prompt_str = "[Admin]> "
            print("Mode admin aktif!")
        else:
            print("Password salah!")
        return None

    # Root mode
    if b.lower() == "root":
        level_akses = "root"
        prompt_str = "[Root]> "
        print("Mode root aktif!")
        return None

    # Kembali ke user
    if b.lower() == "user":
        level_akses = "user"
        prompt_str = "(+)> "
        print("Mode user aktif!")
        return None

    # File Explorer
    if b.startswith("cd "):
        folder = b[3:].strip()
        target = folder if os.path.isabs(folder) else os.path.join(current_folder, folder)
        if os.path.exists(target) and os.path.isdir(target):
            current_folder = os.path.abspath(target)
        else:
            print(f"Folder '{folder}' tidak ditemukan!")
        return None

    if b.startswith("ls"):
        folder = b[3:].strip() or current_folder
        list_files(folder)
        return None

    if b.startswith("cat "):
        file = os.path.join(current_folder, b[4:].strip())
        if os.path.exists(file):
            print(subprocess.getoutput(f"head -n 10 {file}"))
        else:
            print(f"File '{file}' tidak ditemukan!")
        return None

    # Pindah file
    if b.startswith("pindah "):
        parts = b.split()
        if len(parts) < 3: print("Format: pindah <nama_file> <folder_tujuan>"); return None
        file_name = parts[1]; tujuan = parts[2]
        src = os.path.join(DOWNLOADS_FOLDER, file_name)
        if not os.path.exists(src): print(f"File {file_name} tidak ditemukan!"); return None
        os.makedirs(tujuan, exist_ok=True)
        os.rename(src, os.path.join(tujuan, file_name))
        print(f"{file_name} berhasil dipindah ke {tujuan}")
        return None

    # Plugin
    if b.startswith("plugin"):
        if b.strip() == "plugin -m":
            plugins = [f for f in os.listdir(PLUGINS_FOLDER) if f.endswith(".py")]
            for i, p in enumerate(plugins,1): print(f"{i}. {p}")
            choice = input("Pilih plugin untuk aktifkan (nomor): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(plugins):
                path = os.path.join(PLUGINS_FOLDER, plugins[int(choice)-1])
                exec(open(path).read(), globals())
                print("Plugin aktif!")
        elif b.strip() == "plugin -i":
            plugin_name = input("Masukkan nama plugin (.py) untuk auto reload: ").strip()
            if plugin_name in os.listdir(PLUGINS_FOLDER):
                if plugin_name not in AUTO_RELOAD_PLUGINS:
                    AUTO_RELOAD_PLUGINS.append(plugin_name)
                    print(f"{plugin_name} akan di auto reload.")
        return None

    # Jalankan file .blo
    if b.startswith("jalankan "):
        file = b[9:].strip()
        if file.endswith(".blo") and os.path.exists(file):
            kode = open(file).read()
            kode = kode.replace("tulis", "print").replace("masukan", "input").replace("fungsi", "def")
            kode = kode.replace("jika", "if").replace("apabila", "elif").replace("lainnya", "else")
            kode = kode.replace("bulat", "int").replace("pecahan", "float")
            kode = kode.replace("daftar", "list").replace("kamus", "dict")
            kode = kode.replace("kembalikan", "return").replace("Benar","True").replace("Salah","False").replace("Kosong","None")
            try:
                exec(kode, globals(), variabel)
            except Exception as e:
                print("Error:", e)
        else:
            print("File .blo tidak ditemukan!")
        return None

    # Backup
    if b.strip() == "simpan":
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        target = os.path.join(BACKUP_FOLDER, f"backup_{timestamp}")
        os.makedirs(target, exist_ok=True)
        for folder in [DOWNLOADS_FOLDER, PACKAGES_FOLDER]:
            if os.path.exists(folder):
                subprocess.run(f"rsync -a {folder} {target}/", shell=True)
        if os.path.exists(session_file):
            subprocess.run(f"cp {session_file} {target}/", shell=True)
        print(f"Backup selesai di {target}")
        return None

    # Bantuan
    if b.lower() == "bantuan":
        print("Mode akses:", level_akses)
        print("Command dasar:")
        print("cd <folder>, ls, cat <file>, pindah <file> <folder>")
        print("plugin -m, plugin -i, jalankan <file.blo>")
        print("simpan (backup), admin, root, user, bantuan")
        return None

    # Eksekusi perintah shell biasa
    try:
        subprocess.run(b, shell=True, cwd=current_folder)
    except:
        print("Terjadi kesalahan menjalankan:", b)

# ----------------------------
# REPL
# ----------------------------
def repl():
    print("\n=== Ultimate Bahasa Lo REPL ===")
    print("Ketik 'keluar' untuk keluar.")
    while True:
        if current_folder == ".":
            prompt = prompt_str
        else:
            prompt = f"{prompt_str[:-1]} / {os.path.basename(current_folder)}> "
        baris = input(prompt)
        if baris.lower() in ["keluar","exit"]:
            with open(session_file,"wb") as f:
                pickle.dump({"variabel":variabel,"macros":macros},f)
            print("Session tersimpan. Bye!")
            break
        proses_baris(baris)
        reload_plugins()  # auto reload plugin tertentu

if __name__=="__main__":
    repl()
