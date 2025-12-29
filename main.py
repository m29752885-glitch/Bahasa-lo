# main.py - Ultimate Bahasa Lo REPL Final
import os, sys, pickle, subprocess, time
from config.pkg_config import DOWNLOADS_FOLDER, PACKAGES_FOLDER, ADMIN_FOLDER, BACKUP_FOLDER, progress_bar, LOADING_MSGS, PROGRESS_SPEED

# ----------------------------
# Variabel global
# ----------------------------
variabel = {}
macros = {}
alias_perintah = {"Echo": "tulis"}
alias_keyword = {"jika":"if","apabila":"elif","Maka":":"}

prompt_str = "(+)> "
current_folder = "."
user_level = "user"  # user, root, admin

# Plugin settings
PLUGINS_FOLDER = os.path.join(DOWNLOADS_FOLDER, "plugins")
os.makedirs(PLUGINS_FOLDER, exist_ok=True)
active_plugins = ["Explorer_fix.py", "Optimasi.py", "crash_handle.py"]

# Load session sebelumnya
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
# Fungsi log
# ----------------------------
def log(cmd, output=""):
    with open("repl.log","a") as f:
        f.write(f"CMD> {cmd}\n{output}\n")

# ----------------------------
# Evaluasi ekspresi
# ----------------------------
def evaluasi_ekspresi(expr):
    for var in variabel:
        expr = expr.replace(var, str(variabel[var]))
    try:
        return eval(expr)
    except:
        return expr.strip('"')

# ----------------------------
# File Explorer
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
            size_str = f"{size/1024:.1f}K" if size>=1024 else f"{size}B"
            print(f"-rw-r--r-- {size_str:>6} {mtime_str} {entry}")

# ----------------------------
# Proses baris
# ----------------------------
def proses_baris(b):
    global prompt_str, current_folder, user_level

    b = b.strip()
    if b=="" or b.startswith("#"):
        return

    # Masuk Admin
    if b.lower() == "admin":
        password = input("Masukkan password admin: ").strip()
        if password=="12345":
            print("Admin mode aktif! Prompt: [ADMIN]>")
            user_level = "admin"
            prompt_str = "[ADMIN]> "
            return
        else:
            print("Password salah!")
            return

    # Root mode
    if b.lower() == "root":
        user_level = "root"
        prompt_str = "[Root]> "
        print("Mode root aktif!")
        return

    # Keluar dari root/admin
    if b.lower() in ["keluar","exit"]:
        user_level = "user"
        prompt_str = "(+)> "
        print("Kembali ke mode user.")
        return

    # CD
    if b.startswith("cd "):
        folder = b[3:].strip()
        if folder=="..":
            current_folder = os.path.dirname(current_folder)
        else:
            target = os.path.join(current_folder, folder)
            if os.path.exists(target) and os.path.isdir(target):
                current_folder = os.path.abspath(target)
            else:
                print(f"Folder '{folder}' tidak ditemukan!")
        return

    # Shortcut keluar folder
    if b=="keluar_folder":
        current_folder = "."
        return

    # LS
    if b.startswith("ls"):
        folder = b[3:].strip() or current_folder
        list_files(folder)
        return

    # CAT
    if b.startswith("cat "):
        file = os.path.join(current_folder,b[4:].strip())
        if os.path.exists(file):
            print(subprocess.getoutput(f"head -n 10 {file}"))
        else:
            print(f"File '{file}' tidak ditemukan!")
        return

    # Backup
    if b.strip()=="simpan":
        backup_folder = BACKUP_FOLDER
        os.makedirs(backup_folder, exist_ok=True)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        target = os.path.join(backup_folder, f"backup_{timestamp}")
        os.makedirs(target, exist_ok=True)
        for folder in [DOWNLOADS_FOLDER, PACKAGES_FOLDER, PLUGINS_FOLDER]:
            if os.path.exists(folder):
                subprocess.run(f"rsync -a {folder} {target}/", shell=True)
        if os.path.exists(session_file):
            subprocess.run(f"cp {session_file} {target}/", shell=True)
        print(f"Backup selesai! Tersimpan di {target}")
        return

    # Jalankan file .blo
    if b.startswith("jalankan "):
        file = os.path.join(current_folder,b[8:].strip())
        if os.path.exists(file):
            subprocess.run(f"python {file}", shell=True)
        else:
            print(f"File '{file}' tidak ditemukan!")
        return

    # Plugin
    if b.startswith("plugin"):
        if b.strip()=="plugin -m":
            plugins = [f for f in os.listdir(PLUGINS_FOLDER) if f.endswith(".py")]
            if not plugins:
                print("Belum ada plugin.")
            else:
                print("Plugin tersedia:")
                for i,p in enumerate(plugins,1):
                    print(f"{i}. {p}")
                choice = input("Pilih plugin untuk aktifkan (nomor): ").strip()
                if choice.isdigit() and 1<=int(choice)<=len(plugins):
                    plugin_path = os.path.join(PLUGINS_FOLDER,plugins[int(choice)-1])
                    try:
                        exec(open(plugin_path).read(), globals())
                        print("Plugin aktif!")
                    except Exception as e:
                        print("Gagal aktifkan plugin:", e)
            return
        elif b.strip()=="plugin":
            print("Menu Plugin:")
            print("1. Buat file plugin sendiri")
            print("2. Upload dari GitHub")
            choice = input("Pilih opsi: ").strip()
            if choice=="1":
                filename = input("Nama file plugin (.py): ").strip()
                path = os.path.join(PLUGINS_FOLDER, filename)
                with open(path,"w") as f:
                    f.write("# Plugin baru\n")
                print(f"Plugin {filename} berhasil dibuat!")
            elif choice=="2":
                url = input("URL GitHub plugin (.py): ").strip()
                out_file = os.path.join(PLUGINS_FOLDER,url.split("/")[-1])
                subprocess.run(f"wget -O {out_file} {url}", shell=True)
                print(f"Plugin tersimpan di {out_file}")
            return

    # Bantuan
    if b.lower() == "bantuan":
        print("""
Command Dasar:
ls            → tampilkan file/folder
cd <folder>   → masuk folder
cd ..         → naik 1 level
cd /          → ke root
keluar_folder → shortcut ke root
cat <file>    → tampilkan isi file
simpan        → backup semua folder
jalankan <file.blo> → jalankan file .blo
plugin        → menu plugin
plugin -m     → aktifkan plugin
admin         → masuk admin mode
root          → masuk root mode
keluar/exit   → keluar root/rootfs/admin
""")
        return

    # Semua perintah lain
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
    kode_multi=""
    global current_folder, prompt_str
    while True:
        if current_folder==".":
            prompt = prompt_str
        else:
            prompt = f"{prompt_str} / {os.path.basename(current_folder)}> "
        baris = input(prompt)
        if baris.lower() in ["keluar","exit"]:
            with open(session_file,"wb") as f:
                pickle.dump({"variabel":variabel,"macros":macros},f)
            print("Session tersimpan. Bye!")
            break
        proses_baris(baris)

if __name__=="__main__":
    repl()
