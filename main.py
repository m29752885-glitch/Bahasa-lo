#!/usr/bin/env python3
# main.py - Bahasa-Lo REPL Final Full v6 + File Explorer Linux vibes

import os, sys, re, subprocess, pickle, time
from config import pkg_config as cfg

# ----------------------------
# Alias Python → Bahasa Indonesia
# ----------------------------
tulis = print
baca = input
panjang = len
range_id = range
hapus = del
gabung = lambda *args: "".join(args)
ambil = lambda x, y: x[y]

# ----------------------------
# Keywords → bahasa Indonesia (untuk parsing)
# ----------------------------
alias_keyword = {"jika":"if","apabila":"elif","lainnya":"else",
                 "selama":"while","untuk":"for","dalam":"in","Maka":":",
                 "fungsi":"def","kembali":"return"}

# ----------------------------
# Alias perintah
# ----------------------------
alias_perintah = {"Echo":"tulis"}

# ----------------------------
# Variabel global
# ----------------------------
variabel = {}
macros = {}
log_file = "repl.log"
session_file = ".session"
current_folder = "."  # folder aktif
prompt_str = "(+)> "

# ----------------------------
# Pastikan folder ada
# ----------------------------
for folder in [cfg.ROOTFS_FOLDER,cfg.DOWNLOADS_FOLDER,cfg.PACKAGES_FOLDER,cfg.ADMIN_FOLDER,cfg.BACKUP_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# ----------------------------
# Load session sebelumnya
# ----------------------------
if os.path.exists(session_file):
    try:
        with open(session_file,"rb") as f:
            data = pickle.load(f)
            variabel.update(data.get("variabel",{}))
            macros.update(data.get("macros",{}))
        tulis("Session sebelumnya berhasil dimuat.")
    except:
        tulis("Gagal load session, lanjut.")

# ----------------------------
# Fungsi log
# ----------------------------
def log(cmd, output=""):
    with open(log_file,"a") as f:
        f.write(f"CMD> {cmd}\n{output}\n")

# ----------------------------
# Evaluasi ekspresi
# ----------------------------
def evaluasi_ekspresi(expr):
    for var in variabel:
        expr = re.sub(r'\b'+var+r'\b', str(variabel[var]), expr)
    try:
        return eval(expr)
    except:
        return expr.strip('"')

# ----------------------------
# File manager versi Linux vibes clean
# ----------------------------
def list_files(folder=None):
    folder = folder or current_folder
    if not os.path.exists(folder):
        tulis(f"Folder '{folder}' tidak ada!")
        return
    entries = os.listdir(folder)
    for entry in entries:
        path = os.path.join(folder, entry)
        stat = os.stat(path)
        size = stat.st_size
        mtime = time.localtime(stat.st_mtime)
        mtime_str = time.strftime("%b %d %H:%M", mtime)
        if os.path.isdir(path):
            tulis(f"drwxr-xr-x       {mtime_str} {entry}")
        else:
            size_str = f"{size/1024:.1f}K" if size >= 1024 else f"{size}B"
            tulis(f"-rw-r--r-- {size_str:>6} {mtime_str} {entry}")

# ----------------------------
# Proses baris REPL
# ----------------------------
def proses_baris(b):
    b = b.strip()
    global prompt_str, current_folder

    if b == "" or b.startswith("#"):
        return None

    # ----------------------------
    # Admin mode
    # ----------------------------
    if b.lower() == "admin":
        password = baca("Masukkan password admin: ").strip()
        if password=="rahasia123":
            tulis("Mode admin aktif! Pilih menu tweak:")
            tulis("1. Repo GitHub\n2. Repo Linux\n3. Edit mirror pit")
            choice = baca("Pilih opsi: ").strip()
        else:
            tulis("Password salah!")
        return None

    # ----------------------------
    # Proot-distro
    # ----------------------------
    if b.lower() == "linux":
        tulis("Memeriksa distro tersedia...")
        result = subprocess.getoutput("proot-distro list")
        lines = result.splitlines()
        distro_status = {}
        tulis("Distro tersedia:")
        for line in lines:
            line = line.strip()
            if line.startswith("*"):
                name = line[1:].strip()
                tulis(f"{name} (installed)")
                distro_status[name] = True
            elif line:
                tulis(line)
                distro_status[line] = False
        distro = baca("Pilih distro: ").strip()
        if distro:
            if not distro_status.get(distro, False):
                tulis(f"Distro {distro} belum terinstall. Menginstall sekarang...")
                subprocess.run(f"proot-distro install {distro}", shell=True, cwd=cfg.PACKAGES_FOLDER)
                tulis(f"{distro} selesai diinstall!")
            tulis(f"Login ke {distro} ...")
            subprocess.run(f"proot-distro login {distro}", shell=True, cwd=cfg.PACKAGES_FOLDER)
        return None

    # ----------------------------
    # Plugin
    # ----------------------------
    if b.startswith("plugin"):
        if b.strip() == "plugin -m":
            plugins = [f for f in os.listdir(cfg.ADMIN_FOLDER) if f.endswith(".py")]
            if not plugins:
                tulis("Belum ada plugin.")
            else:
                tulis("Plugin tersedia:")
                for i, p in enumerate(plugins,1):
                    tulis(f"{i}. {p}")
                choice = baca("Pilih plugin untuk aktifkan (nomor): ").strip()
                if choice.isdigit() and 1<=int(choice)<=len(plugins):
                    plugin_path = os.path.join(cfg.ADMIN_FOLDER, plugins[int(choice)-1])
                    try:
                        exec(open(plugin_path).read(), globals())
                        tulis("Plugin aktif!")
                    except Exception as e:
                        tulis("Gagal aktifkan plugin:", e)
        elif b.strip()=="plugin":
            tulis("Menu Plugin:\n1. Buat file plugin sendiri\n2. Upload dari GitHub")
            choice = baca("Pilih opsi: ").strip()
            if choice=="1":
                filename = baca("Nama file plugin (.py): ").strip()
                path = os.path.join(cfg.ADMIN_FOLDER, filename)
                with open(path,"w") as f:
                    f.write("# Plugin baru\n")
                tulis(f"Plugin {filename} berhasil dibuat.")
            elif choice=="2":
                url = baca("Masukkan URL GitHub plugin (.py): ").strip()
                out_file = os.path.join(cfg.ADMIN_FOLDER, url.split("/")[-1])
                tulis(f"Download {url} ke {out_file} ...")
                subprocess.run(f"wget -O {out_file} {url}", shell=True)
        return None

    # ----------------------------
    # Jalankan file .blo
    # ----------------------------
    if b.startswith("jalankan "):
        file_blo = os.path.join(current_folder, b[8:].strip())
        if os.path.exists(file_blo):
            with open(file_blo,"r") as f:
                kode = f.read()
            try:
                exec(kode, globals(), variabel)
            except Exception as e:
                tulis("Error:", e)
        else:
            tulis(f"File '{file_blo}' tidak ditemukan!")
        return None

    # ----------------------------
    # Assignment
    # ----------------------------
    if "=" in b and not any(b.startswith(k) for k in ["jika","apabila","selama","untuk"]):
        key,val = b.split("=",1)
        variabel[key.strip()] = evaluasi_ekspresi(val.strip())
        return None

    # ----------------------------
    # Perintah tulis
    # ----------------------------
    for a in alias_perintah:
        if b.startswith(a+" "):
            b = b.replace(a, alias_perintah[a], 1)
    if b.startswith("tulis "):
        isi = b[6:].strip()
        out = evaluasi_ekspresi(isi)
        tulis(out)
        log(b,out)
        return None

    # ----------------------------
    # CD / ls / cat / pindah
    # ----------------------------
    if b.startswith("cd "):
        folder = b[3:].strip()
        if folder=="..":
            current_folder = os.path.abspath(os.path.join(current_folder,".."))
        elif folder=="/":
            current_folder = "."
        else:
            target_path = os.path.join(current_folder, folder)
            if os.path.exists(target_path) and os.path.isdir(target_path):
                current_folder = os.path.abspath(target_path)
            else:
                tulis(f"Folder '{folder}' tidak ditemukan!")
        return None

    if b.strip()=="keluar_folder":
        current_folder = "."
        return None

    if b.startswith("ls"):
        folder = b[3:].strip() or current_folder
        list_files(folder)
        return None

    if b.startswith("cat "):
        file = os.path.join(current_folder, b[4:].strip())
        if os.path.exists(file):
            out = subprocess.getoutput(f"head -n 10 {file}")
            tulis(out)
            log(b,out)
        else:
            tulis(f"File '{file}' tidak ditemukan!")
        return None

    if b.startswith("pindah "):
        parts = b.split()
        if len(parts)<3:
            tulis("Format: pindah <nama_file> <folder_tujuan>")
            return None
        file_name, tujuan = parts[1], parts[2]
        src_path = os.path.join(cfg.DOWNLOADS_FOLDER, file_name)
        if not os.path.exists(src_path):
            tulis(f"File {file_name} tidak ditemukan di downloads/")
            return None
        os.makedirs(tujuan, exist_ok=True)
        dst_path = os.path.join(tujuan, file_name)
        try:
            os.rename(src_path, dst_path)
            tulis(f"{file_name} berhasil dipindah ke {tujuan}/")
        except Exception as e:
            tulis("Gagal memindahkan file:", e)
        return None

    # ----------------------------
    # Root mode
    # ----------------------------
    if b.strip()=="root -a":
        prompt_str = "[Root]> "
        tulis("Prompt REPL sekarang menjadi [Root]>")
        return None

    # ----------------------------
    # Backup
    # ----------------------------
    if b.strip()=="simpan":
        backup_folder = cfg.BACKUP_FOLDER
        os.makedirs(backup_folder, exist_ok=True)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        target = os.path.join(backup_folder,f"backup_{timestamp}")
        os.makedirs(target, exist_ok=True)
        for folder in [cfg.DOWNLOADS_FOLDER,cfg.PACKAGES_FOLDER]:
            if os.path.exists(folder):
                subprocess.run(f"rsync -a {folder} {target}/", shell=True)
        if os.path.exists(session_file):
            subprocess.run(f"cp {session_file} {target}/", shell=True)
        tulis(f"Backup selesai! Tersimpan di {target}")
        return None

    # ----------------------------
    # Bantuan
    # ----------------------------
    if b.lower()=="bantuan":
        tulis("Alias perintah:", alias_perintah)
        tulis("Keyword:", alias_keyword)
        tulis("Macros:", list(macros.keys()))
        tulis("Admin menu: admin")
        tulis("Proot-distro: linux")
        tulis("File/Network: ls, cat, ping, curl, wget, git")
        tulis("Plugin: plugin, plugin -m")
        tulis("File management: pindah <nama_file> <folder_tujuan>")
        tulis("Backup: simpan")
        tulis("Root mode: root -a")
        tulis("Change folder: cd <folder>, cd .., cd /, keluar_folder")
        tulis("Jalankan .blo: jalankan namafile.blo")
        return None

    # ----------------------------
    # Semua command Linux lain
    # ----------------------------
    try:
        subprocess.run(b, shell=True, cwd=current_folder)
        log(b)
    except:
        tulis("Terjadi kesalahan menjalankan:", b)
    return None

# ----------------------------
# REPL
# ----------------------------
def repl():
    tulis("\n=== Ultimate Bahasa Lo REPL Final v6 + Linux File Explorer ===")
    tulis("Ketik 'keluar' untuk keluar.")
    kode_multi=""
    global current_folder, prompt_str
    while True:
        if current_folder==".":
            prompt = "[Root]> " if prompt_str.startswith("[Root]") else "(+)> "
        else:
            prompt = f"[Root]/{os.path.basename(current_folder)}> " if prompt_str.startswith("[Root]") else f"(+) / {os.path.basename(current_folder)}> "
        baris = baca(prompt)
        if baris.lower() in ["keluar","exit"]:
            with open(session_file,"wb") as f:
                pickle.dump({"variabel":variabel,"macros":macros},f)
            tulis("Session tersimpan. Bye!")
            break
        kode = proses_baris(baris)
        if kode:
            kode_multi += kode+"\n"
        if kode_multi and not baris.strip().endswith(":"):
            try:
                exec(kode_multi, globals(), variabel)
            except Exception as e:
                tulis("Error:", e)
            kode_multi = ""

if __name__=="__main__":
    repl()
