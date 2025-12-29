# main.py - Ultimate Bahasa-Lo REPL Final
import os, sys, pickle, subprocess, time, re, glob
from config.pkg_config import DOWNLOADS_FOLDER, PACKAGES_FOLDER, ADMIN_FOLDER, BACKUP_FOLDER, progress_bar, LOADING_MSGS

# ----------------------------
# Variabel global
# ----------------------------
variabel = {}
macros = {}
alias_perintah = {"Echo":"tulis"}
alias_keyword = {"jika":"if","apabila":"elif","Maka":":"}
session_file = ".session"
prompt_str = "(+)> "
current_folder = "."

# ----------------------------
# Pastikan folder ada
# ----------------------------
for folder in [DOWNLOADS_FOLDER, PACKAGES_FOLDER, ADMIN_FOLDER, BACKUP_FOLDER]:
    os.makedirs(folder, exist_ok=True)

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
# Auto-load plugins
# ----------------------------
PLUGINS_FOLDER = "./plugins"
for plugin_file in glob.glob(os.path.join(PLUGINS_FOLDER, "*.py")):
    try:
        exec(open(plugin_file).read(), globals())
        print(f"✅ Plugin '{os.path.basename(plugin_file)}' otomatis aktif!")
    except Exception as e:
        print(f"⚠ Gagal load plugin '{os.path.basename(plugin_file)}':", e)

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
        expr = re.sub(r'\b'+var+r'\b', str(variabel[var]), expr)
    try:
        return eval(expr)
    except:
        return expr.strip('"')

# ----------------------------
# File manager Linux vibes
# ----------------------------
def list_files(folder=None):
    folder = folder or current_folder
    if not os.path.exists(folder):
        print(f"Folder '{folder}' tidak ada!")
        return
    for entry in os.listdir(folder):
        path = os.path.join(folder, entry)
        if os.path.isdir(path):
            print(f"drwxr-xr-x {entry}")
        else:
            size = os.stat(path).st_size
            size_str = f"{size/1024:.1f}K" if size>=1024 else f"{size}B"
            print(f"-rw-r--r-- {size_str:>6} {entry}")

# ----------------------------
# Proses command
# ----------------------------
def proses_baris(b):
    global prompt_str, current_folder

    b = b.strip()
    if not b or b.startswith("#"):
        return None

    # Admin mode
    if b.lower()=="admin":
        password = input("Masukkan password admin: ").strip()
        if password=="12345":
            print("Mode Admin aktif! Pilih opsi:")
            print("1. Tambah repo")
            print("2. Kelola file system utama")
            choice = input("Pilihan: ").strip()
            print(f"Opsi {choice} aktif (implementasi terserah)")
        else:
            print("Password salah!")
        return None

    # Proot-distro
    if b.lower()=="linux":
        print(LOADING_MSGS["check_rootfs"])
        subprocess.run("proot-distro login ubuntu", shell=True)
        return None

    # Jalankan file .blo
    if b.startswith("jalankan "):
        nama_file = b[8:].strip()
        path = os.path.join(current_folder, nama_file)
        if os.path.exists(path):
            with open(path,"r") as f:
                kode = f.read()
            try:
                exec(kode, globals(), variabel)
            except Exception as e:
                print("Error menjalankan file:", e)
        else:
            print(f"File '{nama_file}' tidak ditemukan!")
        return None

    # Alias perintah
    for a in alias_perintah:
        if b.startswith(a+" "):
            b = b.replace(a, alias_perintah[a],1)
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
        print(evaluasi_ekspresi(isi))
        return None

    # File manager commands
    if b.startswith("ls"):
        folder = b[3:].strip() or current_folder
        list_files(folder)
        return None
    if b.startswith("cat "):
        file = os.path.join(current_folder, b[4:].strip())
        if os.path.exists(file):
            out = subprocess.getoutput(f"head -n 10 {file}")
            print(out)
        else:
            print(f"File '{file}' tidak ditemukan!")
        return None
    if b.startswith("cd "):
        folder = b[3:].strip()
        if folder=="..":
            current_folder = os.path.dirname(current_folder)
        elif folder=="/":
            current_folder="."
        else:
            target = os.path.join(current_folder, folder)
            if os.path.isdir(target):
                current_folder = os.path.abspath(target)
            else:
                print(f"Folder '{folder}' tidak ditemukan!")
        return None
    if b.strip()=="keluar_folder":
        current_folder="."
        return None

    # Network commands
    if b.startswith("ping "):
        host = b[5:].strip()
        subprocess.run(f"ping -c 4 {host}", shell=True)
        return None
    if b.startswith("curl "):
        url = b[5:].strip()
        file_out = os.path.join(DOWNLOADS_FOLDER, url.split("/")[-1])
        subprocess.run(f"curl -o {file_out} {url}", shell=True)
        return None
    if b.startswith("wget "):
        url = b[5:].strip()
        file_out = os.path.join(DOWNLOADS_FOLDER, url.split("/")[-1])
        subprocess.run(f"wget -O {file_out} {url}", shell=True)
        return None
    if b.startswith("git "):
        repo = b[4:].strip()
        out_dir = os.path.join(DOWNLOADS_FOLDER, repo.split("/")[-1])
        subprocess.run(f"git clone {repo} {out_dir}", shell=True)
        return None

    # Default: jalankan command Linux
    try:
        subprocess.run(b, shell=True, cwd=current_folder)
    except Exception as e:
        print("Terjadi kesalahan:", e)
    return None

# ----------------------------
# REPL
# ----------------------------
def repl():
    global prompt_str, current_folder
    print("\n=== Bahasa-Lo REPL Final ===")
    print("Ketik 'keluar' untuk keluar.")
    while True:
        prompt = f"[Root]/{os.path.basename(current_folder)}> " if prompt_str.startswith("[Root]") else f"(+)> "
        baris = input(prompt)
        if baris.lower() in ["keluar","exit"]:
            with open(session_file,"wb") as f:
                pickle.dump({"variabel":variabel,"macros":macros}, f)
            print("Session tersimpan. Bye!")
            break
        proses_baris(baris)

if __name__=="__main__":
    repl()
