# main.py - Ultimate Bahasa Lo REPL Final + RootFS Integration
import os, sys, time, pickle, subprocess, re
from config import pkg_config as cfg

# ----------------------------
# Global Variables
# ----------------------------
variabel = {}
macros = {}
alias_perintah = {"Echo":"tulis"}
alias_keyword = {"jika":"if","apabila":"elif","Maka":":"}

log_file = "repl.log"
session_file = ".session"

current_folder = "."  # folder aktif
in_rootfs = False     # apakah sedang di rootfs
prompt_str = "(+)> "

# ----------------------------
# Load session
# ----------------------------
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
# Logging
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
# File Manager (Linux vibes clean)
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
        mtime = time.localtime(stat.st_mtime)
        mtime_str = time.strftime("%b %d %H:%M", mtime)
        if os.path.isdir(path):
            print(f"drwxr-xr-x       {mtime_str} {entry}")
        else:
            size_str = f"{size/1024:.1f}K" if size >= 1024 else f"{size}B"
            print(f"-rw-r--r-- {size_str:>6} {mtime_str} {entry}")

# ----------------------------
# Proses baris
# ----------------------------
def proses_baris(b):
    global current_folder, prompt_str, in_rootfs

    b = b.strip()
    if b == "" or b.startswith("#"):
        return None

    # Admin menu
    if b.lower() == "admin":
        password = input("Masukkan password admin: ").strip()
        if password == "rahasia123":
            print("Mode admin aktif! Pilih menu tweak:")
            print("1. Repo GitHub\n2. Repo Linux / RootFS")
            choice = input("Pilih opsi: ").strip()
            if choice=="1":
                repo = input("Masukkan URL GitHub repo: ").strip()
                out_dir = os.path.join(cfg.DOWNLOADS_FOLDER, repo.split("/")[-1].replace(".git",""))
                print(f"Clone/update {repo} ke {out_dir} ...")
                subprocess.run(f"git clone {repo} {out_dir}", shell=True)
            elif choice=="2":
                print("Belum ada fitur tambahan, rootfs langsung dipakai")
        else:
            print("Password salah!")
        return None

    # RootFS login
    if b.lower() == "linux":
        if not os.path.exists(cfg.ROOTFS_FOLDER):
            print(cfg.LOADING_MSGS["install_rootfs"])
            time.sleep(1)
            print("RootFS belum ada. Silakan download dan extract rootfs manual dulu.")
            return None
        print(cfg.LOADING_MSGS["login_rootfs"])
        in_rootfs = True
        subprocess.run(f"proot -S {cfg.ROOTFS_FOLDER} /bin/bash", shell=True)
        return None

    # Plugin system
    if b.startswith("plugin"):
        plugins_folder = os.path.join(cfg.PACKAGES_FOLDER, "plugins")
        os.makedirs(plugins_folder, exist_ok=True)
        if b.strip() == "plugin -m":
            plugins = [f for f in os.listdir(plugins_folder) if f.endswith(".py")]
            if not plugins:
                print("Belum ada plugin.")
            else:
                print("Plugin tersedia:")
                for i, p in enumerate(plugins, 1):
                    print(f"{i}. {p}")
                choice = input("Pilih plugin untuk aktifkan (nomor): ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(plugins):
                    plugin_path = os.path.join(plugins_folder, plugins[int(choice)-1])
                    try:
                        exec(open(plugin_path).read(), globals())
                        print("Plugin aktif!")
                    except Exception as e:
                        print("Gagal aktifkan plugin:", e)
            return None
        elif b.strip() == "plugin":
            print("Menu Plugin:")
            print("1. Buat file plugin sendiri")
            print("2. Upload dari GitHub")
            choice = input("Pilih opsi: ").strip()
            if choice == "1":
                filename = input("Nama file plugin (.py): ").strip()
                path = os.path.join(plugins_folder, filename)
                with open(path, "w") as f:
                    f.write("# Plugin baru\n")
                print(f"Plugin {filename} berhasil dibuat di folder {plugins_folder}")
            elif choice == "2":
                url = input("Masukkan URL GitHub plugin (.py): ").strip()
                out_file = os.path.join(plugins_folder, url.split("/")[-1])
                subprocess.run(f"wget -O {out_file} {url}", shell=True)
                print(f"Plugin tersimpan di {out_file}")
            return None

    # Macro execution
    if b in macros:
        subprocess.run(macros[b], shell=True)
        return None

    # Ganti alias perintah
    for a in alias_perintah:
        if b.startswith(a+" "):
            b = b.replace(a, alias_perintah[a], 1)
    # Ganti keyword
    for k in alias_keyword:
        b = re.sub(r'\b'+k+r'\b', alias_keyword[k], b)

    # Assignment
    if "=" in b and not b.startswith("if") and not b.startswith("elif"):
        key,val = b.split("=",1)
        variabel[key.strip()] = evaluasi_ekspresi(val.strip())
        return None

    # tulis
    if b.startswith("tulis "):
        isi = b[6:].strip()
        out = evaluasi_ekspresi(isi)
        print(out)
        log(b,out)
        return None

    # CD command
    if b.startswith("cd "):
        folder = b[3:].strip()
        if folder == "/":
            current_folder = "."
        else:
            target_path = os.path.join(current_folder, folder)
            if os.path.exists(target_path) and os.path.isdir(target_path):
                current_folder = os.path.abspath(target_path)
            else:
                print(f"Folder '{folder}' tidak ditemukan!")
        return None

    # Shortcut keluar folder
    if b.strip() == "keluar_folder":
        current_folder = "."
        return None

    # File explorer
    if b.startswith("ls"):
        folder = b[3:].strip() or current_folder
        list_files(folder)
        return None
    if b.startswith("cat "):
        file = os.path.join(current_folder, b[4:].strip())
        if os.path.exists(file):
            out = subprocess.getoutput(f"head -n 10 {file}")
            print(out)
            log(b,out)
        else:
            print(f"File '{file}' tidak ditemukan!")
        return None

    # Network tools
    if b.startswith("ping "):
        host = b[5:].strip()
        subprocess.run(f"ping -c 4 {host}", shell=True)
        return None
    if b.startswith("curl "):
        url = b[5:].strip()
        filename = url.split("/")[-1]
        folder = cfg.PACKAGES_FOLDER if in_rootfs else cfg.DOWNLOADS_FOLDER
        out_file = os.path.join(folder, filename)
        print(cfg.LOADING_MSGS["download_file"])
        subprocess.run(f"curl -o {out_file} {url}", shell=True)
        return None
    if b.startswith("wget "):
        url = b[5:].strip()
        filename = url.split("/")[-1]
        folder = cfg.PACKAGES_FOLDER if in_rootfs else cfg.DOWNLOADS_FOLDER
        out_file = os.path.join(folder, filename)
        print(cfg.LOADING_MSGS["download_file"])
        subprocess.run(f"wget -O {out_file} {url}", shell=True)
        return None
    if b.startswith("git "):
        repo_url = b[4:].strip()
        repo_name = repo_url.split("/")[-1].replace(".git","")
        folder = cfg.PACKAGES_FOLDER if in_rootfs else cfg.DOWNLOADS_FOLDER
        out_dir = os.path.join(folder, repo_name)
        print(cfg.LOADING_MSGS["download_file"])
        subprocess.run(f"git clone {repo_url} {out_dir}", shell=True)
        return None

    # Jalankan file .blo
    if b.startswith("jalankan "):
        file = os.path.join(current_folder, b[9:].strip())
        if os.path.exists(file):
            try:
                exec(open(file).read(), globals(), variabel)
            except Exception as e:
                print("Error saat menjalankan file:", e)
        else:
            print(f"File '{file}' tidak ditemukan!")
        return None

    # Backup
    if b.strip() == "simpan":
        backup_folder = os.path.join(cfg.BACKUP_FOLDER, time.strftime("%Y%m%d-%H%M%S"))
        os.makedirs(backup_folder, exist_ok=True)
        for folder in [cfg.DOWNLOADS_FOLDER, cfg.PACKAGES_FOLDER]:
            if os.path.exists(folder):
                subprocess.run(f"rsync -a {folder} {backup_folder}/", shell=True)
        if os.path.exists(session_file):
            subprocess.run(f"cp {session_file} {backup_folder}/", shell=True)
        print(f"Backup selesai! Tersimpan di {backup_folder}")
        return None

    # Root mode
    if b.strip() == "root -a":
        prompt_str = "[Root]> "
        print("Prompt REPL sekarang menjadi [Root]>")
        return None

    # Bantuan
    if b.lower() == "bantuan":
        print("Alias perintah:", alias_perintah)
        print("Keyword:", alias_keyword)
        print("Macros:", list(macros.keys()))
        print("Admin menu: admin")
        print("RootFS: linux")
        print("File/Network: ls, cat, ping, curl, wget, git")
        print("Plugin: plugin, plugin -m")
        print("File management: pindah <nama_file> <folder_tujuan>")
        print("Backup: simpan")
        print("Root mode: root -a")
        print("Change folder: cd <folder>, cd .. (naik 1 level), cd / (root REPL), keluar_folder (shortcut ke root)")
        print("Jalankan file .blo: jalankan <file.blo>")
        return None

    # Semua perintah Linux lain
    try:
        subprocess.run(b, shell=True, cwd=current_folder)
        log(b)
    except:
        print("Terjadi kesalahan menjalankan:", b)
    return None

# ----------------------------
# REPL
# ----------------------------
def repl():
    print("\n=== Ultimate Bahasa Lo REPL + RootFS ===")
    print("Ketik 'keluar' untuk keluar.")
    kode_multi=""
    global current_folder, prompt_str
    while True:
        if current_folder == ".":
            prompt = "[Root]> " if prompt_str.startswith("[Root]") else "(+)> "
        else:
            prompt = f"[Root]/{os.path.basename(current_folder)}> " if prompt_str.startswith("[Root]") else f"(+) / {os.path.basename(current_folder)}> "
        baris = input(prompt)
        if baris.lower() in ["keluar","exit"]:
            with open(session_file,"wb") as f:
                pickle.dump({"variabel":variabel,"macros":macros},f)
            print("Session tersimpan. Bye!")
            break
        kode = proses_baris(baris)
        if kode:
            kode_multi += kode+"\n"
        if kode_multi and not baris.strip().endswith(":"):
            try:
                exec(kode_multi, globals(), variabel)
            except Exception as e:
                print("Error:", e)
            kode_multi = ""

if __name__=="__main__":
    repl()
