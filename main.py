# main.py – Bahasa-lo REPL Full Final
import os, re, subprocess, pickle, time, sys

# ----------------------------
# Load config
# ----------------------------
from config import pkg_config, pit_config

alias_perintah = pkg_config.alias_perintah
alias_keyword = pkg_config.alias_keyword
macros = pkg_config.macros

downloads_folder = pkg_config.downloads_folder
packages_folder = pkg_config.packages_folder
plugins_folder = pkg_config.plugins_folder
backup_folder = pkg_config.backup_folder
session_file = pkg_config.session_file
log_file = pkg_config.log_file

os.makedirs(downloads_folder, exist_ok=True)
os.makedirs(packages_folder, exist_ok=True)
os.makedirs(plugins_folder, exist_ok=True)
os.makedirs(backup_folder, exist_ok=True)

prompt_str = "(+)> "
current_folder = "."

# ----------------------------
# Progress bar sederhana
# ----------------------------
def progress_bar(task_name, duration=1):
    print(f"{task_name}...", end="")
    sys.stdout.flush()
    for i in range(20):
        print("█", end="")
        sys.stdout.flush()
        time.sleep(duration/20)
    print(" Done!")

# ----------------------------
# Load session
# ----------------------------
if os.path.exists(session_file):
    try:
        with open(session_file,"rb") as f:
            data = pickle.load(f)
            # Load variabel & macros
            globals().update(data.get("variabel",{}))
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
# Admin menu (repo/mirror tweak)
# ----------------------------
def admin_menu():
    password = input("Masukkan password admin: ").strip()
    if password != "rahasia123":
        print("Password salah!")
        return
    while True:
        print("\n=== Admin Menu ===")
        print("1. Repo GitHub")
        print("2. Repo Linux")
        print("3. Repo Pit (Termux)")
        print("0. Keluar")
        choice = input("Pilih opsi: ").strip()
        if choice == "0":
            break
        elif choice == "3":
            while True:
                print("\n=== Pit Repo Menu ===")
                print("1. Lihat repo list")
                print("2. Tambah package")
                print("3. Hapus package")
                print("4. Lihat mirror")
                print("5. Tambah mirror")
                print("6. Hapus mirror")
                print("0. Keluar")
                sub = input("Pilih opsi: ").strip()
                if sub == "1":
                    for i,pkg in enumerate(pit_config.repo_list,1):
                        print(f"{i}. {pkg}")
                elif sub == "2":
                    nama = input("Nama package: ").strip()
                    url = input("URL package: ").strip()
                    arch = input("Arsitektur (arm64/all): ").strip()
                    pit_config.repo_list.append(f"{nama} | {url} | {arch} | termux")
                    print(f"{nama} ditambahkan ke repo list!")
                elif sub == "3":
                    idx = int(input("Nomor package untuk hapus: ").strip())
                    if 1 <= idx <= len(pit_config.repo_list):
                        hapus = pit_config.repo_list.pop(idx-1)
                        print(f"{hapus} dihapus!")
                elif sub == "4":
                    for i,m in enumerate(pit_config.mirrors,1):
                        print(f"{i}. {m}")
                elif sub == "5":
                    m = input("URL mirror baru: ").strip()
                    pit_config.mirrors.append(m)
                    print(f"Mirror {m} ditambahkan!")
                elif sub == "6":
                    idx = int(input("Nomor mirror untuk hapus: ").strip())
                    if 1 <= idx <= len(pit_config.mirrors):
                        hapus = pit_config.mirrors.pop(idx-1)
                        print(f"Mirror {hapus} dihapus!")
                elif sub == "0":
                    break
        else:
            print("Opsi belum implementasi")

# ----------------------------
# REPL Proses Baris
# ----------------------------
def proses_baris(b):
    global prompt_str, current_folder
    b = b.strip()
    if b == "" or b.startswith("#"):
        return None

    # Admin
    if b.lower() == "admin":
        admin_menu()
        return None

    # tulis (print)
    for a in alias_perintah:
        if b.startswith(a+" "):
            b = b.replace(a, alias_perintah[a], 1)
    for k in alias_keyword:
        b = re.sub(r'\b'+k+r'\b', alias_keyword[k], b)
    if b.startswith("tulis "):
        isi = b[6:].strip()
        out = evaluasi_ekspresi(isi)
        print(out)
        log(b,out)
        return None

    # cd / ls / cat
    if b.startswith("cd "):
        folder = b[3:].strip()
        if folder == "/":
            current_folder = "."
        else:
            target = os.path.join(current_folder, folder)
            if os.path.isdir(target):
                current_folder = os.path.abspath(target)
            else:
                print(f"Folder '{folder}' tidak ditemukan!")
        return None
    if b.strip() == "keluar_folder":
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
            print(out)
            log(b,out)
        else:
            print(f"File '{file}' tidak ditemukan!")
        return None

    # jalankan .blo
    if b.startswith("jalankan "):
        file = os.path.join(current_folder, b[8:].strip())
        if os.path.exists(file):
            try:
                with open(file) as f:
                    kode = f.read()
                exec(kode, globals())
            except Exception as e:
                print("Error menjalankan .blo:", e)
        else:
            print(f"{file} tidak ditemukan!")
        return None

    # Linux / shell lain
    try:
        subprocess.run(b, shell=True, cwd=current_folder)
        log(b)
    except:
        print("Terjadi kesalahan:", b)
    return None

# ----------------------------
# REPL Loop
# ----------------------------
def repl():
    print("=== Bahasa-lo REPL Full Final ===")
    print("Ketik 'keluar' untuk keluar.")
    global prompt_str, current_folder
    while True:
        prompt = "[Root]> " if prompt_str.startswith("[Root]") else "(+)> "
        if current_folder != ".":
            prompt = f"(+) / {os.path.basename(current_folder)}> "
        baris = input(prompt)
        if baris.lower() in ["keluar","exit"]:
            with open(session_file,"wb") as f:
                pickle.dump({"variabel":globals(), "macros":macros}, f)
            print("Session tersimpan. Bye!")
            break
        proses_baris(baris)

# ----------------------------
# MAIN
# ----------------------------
if __name__=="__main__":
    repl()
