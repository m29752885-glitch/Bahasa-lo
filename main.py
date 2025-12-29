# main.py - Ultimate Bahasa Lo REPL Final

import os, sys, time, subprocess, pickle

# ----------------------------
# Config
# ----------------------------
from config.pkg_config import DOWNLOADS_FOLDER, PACKAGES_FOLDER, ADMIN_FOLDER, BACKUP_FOLDER, progress_bar, LOADING_MSGS, PROGRESS_SPEED

os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)
os.makedirs(PACKAGES_FOLDER, exist_ok=True)
os.makedirs(ADMIN_FOLDER, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)

# ----------------------------
# Variables
# ----------------------------
variabel = {}
macros = {}
session_file = ".session"
current_folder = "."
prompt_str = "(+)> "
LEVEL = "user"  # user/root/admin

# ----------------------------
# Plugin system
# ----------------------------
PLUGINS_FOLDER = os.path.join(DOWNLOADS_FOLDER,"plugins")
AUTO_RELOAD_PLUGINS = ["Explorer_fix.py","Optimasi.py","crash_handle.py"]
os.makedirs(PLUGINS_FOLDER, exist_ok=True)

def load_plugins():
    plugins = [f for f in os.listdir(PLUGINS_FOLDER) if f.endswith(".py")]
    for plugin in plugins:
        if plugin in AUTO_RELOAD_PLUGINS:
            try:
                exec(open(os.path.join(PLUGINS_FOLDER, plugin)).read(), globals())
                print(f"Plugin {plugin} auto-reload aktif!")
            except Exception as e:
                print("Gagal load plugin:", plugin, e)

def menu_plugin_manual():
    plugins = [f for f in os.listdir(PLUGINS_FOLDER) if f.endswith(".py")]
    if not plugins:
        print("Belum ada plugin.")
        return
    print("Plugin tersedia:")
    for i, p in enumerate(plugins, 1):
        print(f"{i}. {p}")
    choice = input("Pilih plugin untuk aktifkan (nomor): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(plugins):
        plugin_path = os.path.join(PLUGINS_FOLDER, plugins[int(choice)-1])
        print(f"Mengaktifkan plugin {plugins[int(choice)-1]} ...")
        try:
            exec(open(plugin_path).read(), globals())
            print("Plugin aktif!")
        except Exception as e:
            print("Gagal aktifkan plugin:", e)

# Load auto-reload plugin di awal
load_plugins()

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
# Utility functions
# ----------------------------
def log(cmd, output=""):
    with open("repl.log","a") as f:
        f.write(f"CMD> {cmd}\n{output}\n")

def evaluasi_ekspresi(expr):
    for var in variabel:
        expr = expr.replace(var,str(variabel[var]))
    try:
        return eval(expr)
    except:
        return expr.strip('"')

def list_files(folder=None):
    folder = folder or current_folder
    if not os.path.exists(folder):
        print(f"Folder '{folder}' tidak ada!")
        return
    for entry in os.listdir(folder):
        path = os.path.join(folder,entry)
        size = os.stat(path).st_size
        mtime = time.localtime(os.stat(path).st_mtime)
        mtime_str = time.strftime("%b %d %H:%M", mtime)
        if os.path.isdir(path):
            print(f"drwxr-xr-x       {mtime_str} {entry}")
        else:
            size_str = f"{size/1024:.1f}K" if size>=1024 else f"{size}B"
            print(f"-rw-r--r-- {size_str:>6} {mtime_str} {entry}")

# ----------------------------
# Process REPL commands
# ----------------------------
def proses_baris(b):
    global current_folder, prompt_str, LEVEL

    b = b.strip()
    if b=="" or b.startswith("#"): return None

    # Admin mode
    if b.lower()=="admin":
        password = input("Masukkan password admin: ").strip()
        if password=="12345":
            LEVEL="admin"
            print("Mode ADMIN aktif!")
            return None
        else:
            print("Password salah!")
            return None

    # Proot-distro Linux
    if b.lower()=="linux":
        result = subprocess.getoutput("proot-distro list")
        lines = result.splitlines()
        print("Distro tersedia:")
        distro_status = {}
        for line in lines:
            line=line.strip()
            if line.startswith("*"):
                name = line[1:].strip()
                print(f"{name} (diinstal)")
                distro_status[name]=True
            elif line:
                print(line)
                distro_status[line]=False
        distro = input("Pilih distro: ").strip()
        if distro:
            if not distro_status.get(distro,False):
                print(f"Install {distro}...")
                subprocess.run(f"proot-distro install {distro}", shell=True)
            print(f"Login ke {distro} ...")
            subprocess.run(f"proot-distro login {distro}", shell=True)
        return None

    # Plugin system
    if b.startswith("plugin"):
        if b.strip()=="plugin -m":
            menu_plugin_manual()
        elif b.strip()=="plugin -i":
            load_plugins()
        return None

    # Assignment
    if "=" in b and not b.startswith("if") and not b.startswith("elif"):
        key,val = b.split("=",1)
        variabel[key.strip()]=evaluasi_ekspresi(val.strip())
        return None

    # tulis
    if b.startswith("tulis "):
        isi = b[6:].strip()
        out = evaluasi_ekspresi(isi)
        print(out)
        log(b,out)
        return None

    # cd command
    if b.startswith("cd "):
        folder = b[3:].strip()
        if folder=="/":
            current_folder="."
        else:
            target = os.path.join(current_folder, folder)
            if os.path.exists(target) and os.path.isdir(target):
                current_folder=os.path.abspath(target)
            else:
                print(f"Folder '{folder}' tidak ditemukan!")
        return None

    if b=="keluar_folder":
        current_folder="."
        return None

    # ls / cat
    if b.startswith("ls"):
        folder = b[3:].strip() or current_folder
        list_files(folder)
        return None

    if b.startswith("cat "):
        file = os.path.join(current_folder,b[4:].strip())
        if os.path.exists(file):
            out = subprocess.getoutput(f"head -n 10 {file}")
            print(out)
            log(b,out)
        else:
            print(f"File '{file}' tidak ditemukan!")
        return None

    # .blo interpreter
    if b.startswith("jalankan "):
        file = os.path.join(current_folder,b[8:].strip())
        if os.path.exists(file):
            try:
                with open(file) as f:
                    exec(f.read(), globals())
            except Exception as e:
                print("Error jalankan .blo:", e)
        else:
            print(f"File '{file}' tidak ditemukan!")
        return None

    # semua command Linux lain
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
    global current_folder, prompt_str, LEVEL
    print("\n=== Ultimate Bahasa Lo REPL Final ===")
    print("Ketik 'keluar' untuk keluar.")
    while True:
        if current_folder==".":
            prompt = "[ADMIN]> " if LEVEL=="admin" else "(+)> "
        else:
            prompt = f"[ADMIN]/{os.path.basename(current_folder)}> " if LEVEL=="admin" else f"(+) / {os.path.basename(current_folder)}> "
        baris = input(prompt)
        if baris.lower() in ["keluar","exit"]:
            with open(session_file,"wb") as f:
                pickle.dump({"variabel":variabel,"macros":macros},f)
            print("Session tersimpan. Bye!")
            break
        proses_baris(baris)

if __name__=="__main__":
    repl()
