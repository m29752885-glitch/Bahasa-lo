# main.py - Ultimate Bahasa Lo REPL Final

import os, sys, time, pickle, subprocess
from config.pkg_config import DOWNLOADS_FOLDER, PACKAGES_FOLDER, ADMIN_FOLDER, BACKUP_FOLDER, progress_bar, LOADING_MSGS, PROGRESS_SPEED


# =========================
# Alias Python Bahasa Indonesia
# =========================

tulis = print
masukan = input
bulat = int
pecahan = float
panjang = len
daftar = list
kamus = dict

Benar = True
Salah = False
Kosong = None

# ----------------------------
# Variabel global
# ----------------------------
variabel = {}
macros = {}
alias_perintah = {"Echo":"tulis"}
alias_keyword = {"jika":"if","apabila":"elif","Maka":":"}
plugins_folder = os.path.join(DOWNLOADS_FOLDER, "plugins")
os.makedirs(plugins_folder, exist_ok=True)

prompt_str = "(+)> "
current_folder = "."
user_level = "user"  # user/root/admin

# ----------------------------
# Load session sebelumnya
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
# Log function
# ----------------------------
log_file = "repl.log"
def log(cmd, output=""):
    with open(log_file,"a") as f:
        f.write(f"CMD> {cmd}\n{output}\n")

# ----------------------------
# Evaluasi ekspresi
# ----------------------------
import re
def evaluasi_ekspresi(expr):
    for var in variabel:
        expr = re.sub(r'\b'+var+r'\b', str(variabel[var]), expr)
    try:
        return eval(expr)
    except:
        return expr.strip('"')

# ----------------------------
# File Explorer vibe Linux
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
# Menu bantuan
# ----------------------------
def menu_bantuan():
    tulis("\n=== Bantuan Ultimate Bahasa Lo REPL ===")
    tulis("Perintah Python (Bahasa Indonesia):")
    tulis("  tulis <isi>        → print")
    tulis("  masukan <prompt>   → input")
    tulis("  bulat(<nilai>)     → int")
    tulis("  pecahan(<nilai>)   → float")
    tulis("  daftar(<nilai>)    → list")
    tulis("  kamus(<nilai>)     → dict")
    tulis("  jika / apabila / lainnya → if / elif / else")
    tulis("  untuk → for")
    tulis("  fungsi ... kembalikan ... → def ... return ...")
    tulis("  Benar / Salah / Kosong → True / False / None")
    tulis("\nPerintah File Explorer:")
    tulis("  ls [folder]       → list file di folder")
    tulis("  cd <folder>       → masuk folder")
    tulis("  cd /              → ke root REPL")
    tulis("  keluar_folder     → shortcut ke root REPL")
    tulis("  cat <file>        → lihat isi file (10 baris)")
    tulis("\nJalankan file .blo:")
    tulis("  jalankan <file.blo> → menjalankan file .blo")
    tulis("\nMode & Prompt:")
    tulis("  admin             → login mode admin")
    tulis("  root -a           → ganti ke root prompt")
    tulis("  user              → ganti ke user prompt")
    tulis("\nPlugins:")
    tulis("  plugins auto-load saat REPL start")
    tulis("\nLain-lain:")
    tulis("  simpan            → backup downloads / packages / plugins / session")
    tulis("  keluar / exit     → keluar REPL\n")

# ----------------------------
# Proses baris REPL
# ----------------------------
def proses_baris(b):
    global current_folder, prompt_str, user_level
    b = b.strip()
    if b=="" or b.startswith("#"):
        return None

    # Bantuan
    if b.lower() == "bantuan":
        menu_bantuan()
        return None

    # Admin mode
    if b.lower() == "admin":
        pw = masukan("Password admin: ").strip()
        if pw == "12345":
            user_level = "admin"
            prompt_str = "[Admin]> "
            tulis("Admin mode aktif!")
        else:
            tulis("Password salah!")
        return None

    # Root mode
    if b.strip() == "root -a":
        user_level = "root"
        prompt_str = "[Root]> "
        tulis("Prompt sekarang root!")
        return None

    # User mode
    if b.strip() == "user":
        user_level = "user"
        prompt_str = "(+)> "
        tulis("Prompt sekarang user biasa!")
        return None

    # Jalankan .blo
    if b.startswith("jalankan "):
        file_path = os.path.join(current_folder, b[9:].strip())
        if os.path.exists(file_path):
            with open(file_path,"r") as f:
                kode = f.read()
            try:
                exec(kode, globals(), variabel)
            except Exception as e:
                tulis("Error:", e)
        else:
            tulis("File tidak ditemukan!")
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
        out = evaluasi_ekspresi(b[6:].strip())
        print(out)
        log(b,out)
        return None

    # cd
    if b.startswith("cd "):
        folder = b[3:].strip()
        if folder == "/":
            current_folder = "."
        else:
            target_path = os.path.join(current_folder, folder)
            if os.path.exists(target_path) and os.path.isdir(target_path):
                current_folder = os.path.abspath(target_path)
            else:
                tulis(f"Folder '{folder}' tidak ditemukan!")
        return None

    if b.strip() == "keluar_folder":
        current_folder = "."
        return None

    # ls
    if b.startswith("ls"):
        folder = b[3:].strip() or current_folder
        list_files(folder)
        return None

    # cat
    if b.startswith("cat "):
        file = os.path.join(current_folder, b[4:].strip())
        if os.path.exists(file):
            out = subprocess.getoutput(f"head -n 10 {file}")
            print(out)
            log(b,out)
        else:
            tulis(f"File '{file}' tidak ditemukan!")
        return None

    # Jalankan command Linux lain
    try:
        subprocess.run(b, shell=True, cwd=current_folder)
        log(b)
    except:
        tulis("Terjadi kesalahan menjalankan:",b)
    return None

# ----------------------------
# REPL
# ----------------------------
def repl():
    tulis("\n=== Ultimate Bahasa Lo REPL ===")
    tulis("Ketik 'bantuan' untuk daftar perintah.")
    kode_multi=""
    global current_folder, prompt_str
    while True:
        if current_folder == ".":
            prompt = prompt_str
        else:
            prompt = f"{prompt_str}{os.path.basename(current_folder)}> "
        baris = masukan(prompt)
        if baris.lower() in ["keluar","exit"]:
            with open(".session","wb") as f:
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
