# main.py - Ultimate Bahasa-Lo REPL Final
import os, sys, subprocess, time, pickle
from config.pkg_config import DOWNLOADS_FOLDER, PACKAGES_FOLDER, ADMIN_FOLDER, BACKUP_FOLDER, progress_bar, LOADING_MSGS, PROGRESS_SPEED

# ----------------------------
# Variabel global
# ----------------------------
variabel = {}
macros = {}
alias_perintah = {"Echo":"tulis"}
alias_keyword = {"jika":"if","apabila":"elif","Maka":":"}
log_file = "repl.log"
session_file = ".session"
PLUGINS_FOLDER = os.path.join(DOWNLOADS_FOLDER,"plugins")
os.makedirs(PLUGINS_FOLDER, exist_ok=True)
prompt_str = "(+)> "
current_folder = "."
akses_level = "user"  # user, root, admin
# Alias Python → Bahasa Indonesia
tulis = print
masukan = input
bulat = int
pecahan = float
daftar = list
kamus = dict
Benar = True
Salah = False
Kosong = None

# ----------------------------
# Load session sebelumnya
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
# Log function
# ----------------------------
def log(cmd, output=""):
    with open(log_file,"a") as f:
        f.write(f"CMD> {cmd}\n{output}\n")

# ----------------------------
# Evaluasi ekspresi
# ----------------------------
def evaluasi_ekspresi(expr):
    for var in variabel:
        expr = expr.replace(var,str(variabel[var]))
    try:
        return eval(expr)
    except:
        return expr.strip('"')

# ----------------------------
# File manager Linux vibe
# ----------------------------
def list_files(folder=None):
    folder = folder or current_folder
    if not os.path.exists(folder):
        print(f"Folder '{folder}' tidak ada!")
        return
    entries = os.listdir(folder)
    for entry in entries:
        path = os.path.join(folder,entry)
        stat = os.stat(path)
        size = stat.st_size
        mtime = time.strftime("%b %d %H:%M", time.localtime(stat.st_mtime))
        if os.path.isdir(path):
            print(f"drwxr-xr-x       {mtime} {entry}")
        else:
            size_str = f"{size/1024:.1f}K" if size >= 1024 else f"{size}B"
            print(f"-rw-r--r-- {size_str:>6} {mtime} {entry}")

# ----------------------------
# Plugin auto reload setup
# ----------------------------
AUTO_RELOAD_PLUGINS = ["Explorer_fix.py","Optimasi.py","crash_handle.py"]
aktif_plugins = {}

def load_plugin(plugin_file):
    path = os.path.join(PLUGINS_FOLDER,plugin_file)
    if os.path.exists(path):
        try:
            exec(open(path).read(), globals())
            aktif_plugins[plugin_file] = True
        except Exception as e:
            print(f"Gagal load plugin {plugin_file}: {e}")

# ----------------------------
# REPL command processor
# ----------------------------
def proses_baris(b):
    global prompt_str, current_folder, akses_level

    b = b.strip()
    if b=="" or b.startswith("#"):
        return None

    # Admin mode
    if b.lower()=="admin":
        pw = input("Masukkan password admin: ").strip()
        if pw=="12345":
            akses_level = "admin"
            prompt_str = "[Admin]> "
            print("Mode admin aktif!")
        else:
            print("Password salah!")
        return None

    # Root mode
    if b.lower()=="root -a":
        akses_level="root"
        prompt_str = "[Root]> "
        print("Prompt REPL sekarang menjadi [Root]>")
        return None

    # Keluar dari root/admin
    if b.lower() in ["keluar_root","keluar_admin"]:
        akses_level="user"
        prompt_str="(+)> "
        print("Kembali ke mode user.")
        return None

    # Plugin menu
    if b.startswith("plugin"):
        if "-m" in b:
            plugins = [f for f in os.listdir(PLUGINS_FOLDER) if f.endswith(".py")]
            if not plugins:
                print("Belum ada plugin.")
            else:
                print("Plugin tersedia:")
                for i,p in enumerate(plugins,1):
                    print(f"{i}. {p}")
                choice = input("Pilih plugin untuk aktifkan (nomor): ").strip()
                if choice.isdigit() and 1<=int(choice)<=len(plugins):
                    load_plugin(plugins[int(choice)-1])
                    print(f"Plugin {plugins[int(choice)-1]} aktif!")
        elif "-i" in b:
            plugins = [f for f in os.listdir(PLUGINS_FOLDER) if f.endswith(".py")]
            print("Auto reload plugin sekarang hanya untuk:", plugins)
        else:
            print("Menu Plugin:")
            print("1. Buat file plugin sendiri")
            print("2. Upload dari GitHub")
        return None

    # Bantuan
    if b.lower()=="bantuan":
        print("Fitur & command:")
        print("User prompt biasa, akses terbatas.")
        print("Admin prompt penuh akses, password: 12345")
        print("Root prompt akses sistem.")
        print("File/Network: ls, cd <folder>, cat <file>, pindah <file> <folder>")
        print("Plugin: plugin, plugin -m, plugin -i")
        print("Backup: simpan")
        print("Root: root -a, keluar_root")
        print("Admin: admin, keluar_admin")
        print("Blo interpreter: jalankan <file>.blo")
        return None

    # CD command
    if b.startswith("cd "):
        folder = b[3:].strip()
        target = folder if folder=="/" else os.path.join(current_folder,folder)
        if os.path.exists(target) and os.path.isdir(target):
            current_folder = os.path.abspath(target)
        else:
            print(f"Folder '{folder}' tidak ditemukan!")
        return None

    # Keluar folder shortcut
    if b.strip()=="keluar_folder":
        current_folder="."
        return None

    # File Explorer
    if b.startswith("ls"):
        folder = b[3:].strip() or current_folder
        list_files(folder)
        return None
    if b.startswith("cat "):
        file = os.path.join(current_folder,b[4:].strip())
        if os.path.exists(file):
            out = subprocess.getoutput(f"head -n 10 {file}")
            print(out)
        else:
            print(f"File '{file}' tidak ditemukan!")
        return None

    # Backup
    if b.strip()=="simpan":
        ts = time.strftime("%Y%m%d-%H%M%S")
        backup_dir = os.path.join(BACKUP_FOLDER,f"backup_{ts}")
        os.makedirs(backup_dir,exist_ok=True)
        for folder in [DOWNLOADS_FOLDER,PACKAGES_FOLDER,PLUGINS_FOLDER]:
            subprocess.run(f"rsync -a {folder} {backup_dir}/",shell=True)
        if os.path.exists(session_file):
            subprocess.run(f"cp {session_file} {backup_dir}/",shell=True)
        print(f"Backup selesai! Tersimpan di {backup_dir}")
        return None

    # Jalankan .blo
    if b.startswith("jalankan "):
        file = b[9:].strip()
        path = os.path.join(current_folder,file)
        if os.path.exists(path):
            exec(open(path).read(),globals())
        else:
            print(f"File {file} tidak ditemukan!")
        return None

    # Evaluasi Python
    try:
        exec(b,globals(),variabel)
    except Exception as e:
        print("Error:",e)

# ----------------------------
# REPL
# ----------------------------
def repl():
    print("\n=== Ultimate Bahasa Lo REPL ===")
    print("Ketik 'keluar' untuk keluar.")
    for plugin in AUTO_RELOAD_PLUGINS:
        load_plugin(plugin)
    while True:
        prompt = prompt_str if current_folder=="." else f"{prompt_str}{os.path.basename(current_folder)}> "
        baris = input(prompt)
        if baris.lower() in ["keluar","exit"]:
            with open(session_file,"wb") as f:
                pickle.dump({"variabel":variabel,"macros":macros},f)
            print("Session tersimpan. Bye!")
            break
        proses_baris(baris)

if __name__=="__main__":
    repl()
