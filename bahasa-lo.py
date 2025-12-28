# Ultimate REPL Final v5 – Full Final Script
import re, subprocess, time, sys, os, pickle

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
# Auto-install package penting
# ----------------------------
required_packages = ["rsync","apt-mirror","git","wget","curl","proot-distro"]
for pkg in required_packages:
    try:
        print(f"\nMemeriksa package '{pkg}'...")
        subprocess.run(f"apt install -y {pkg}", shell=True)
        progress_bar(f"Installing {pkg}", 0.5)
    except:
        print(f"Gagal install {pkg}, lanjut saja")

# ----------------------------
# Setup global
# ----------------------------
variabel = {}
alias_perintah = {"Echo":"tulis"}
alias_keyword = {"jika":"if","apabila":"elif","Maka":":"}
macros = {}
log_file = "repl.log"
session_file = ".session"
downloads_folder = "./downloads"
plugins_folder = os.path.join(downloads_folder, "plugins")
os.makedirs(downloads_folder, exist_ok=True)
os.makedirs(plugins_folder, exist_ok=True)
prompt_str = "(+)> "
current_folder = "."  # folder aktif

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
# Proses perintah
# ----------------------------
def proses_baris(b):
    b = b.strip()
    if b == "" or b.startswith("#"):
        return None

    global prompt_str, current_folder

    # Admin mode
    if b.lower() == "admin":
        password = input("Masukkan password admin: ").strip()
        if password == "rahasia123":
            print("Mode admin aktif! Pilih menu tweak:")
            print("1. Repo GitHub\n2. Repo Linux")
            choice = input("Pilih opsi: ").strip()
            if choice=="1":
                repo = input("Masukkan URL GitHub repo: ").strip()
                out_dir = os.path.join(downloads_folder, repo.split("/")[-1].replace(".git",""))
                print(f"Clone/update {repo} ke {out_dir} ...")
                subprocess.run(f"git clone {repo} {out_dir}", shell=True)
            elif choice=="2":
                print("1. Update paket\n2. Mirror repo Linux")
                sub = input("Pilih opsi: ").strip()
                if sub=="1":
                    subprocess.run("apt update && apt upgrade -y", shell=True)
                elif sub=="2":
                    repo_url = input("Masukkan URL repo: ").strip()
                    folder = input("Folder tujuan mirror: ").strip()
                    subprocess.run(f"rsync -av --progress {repo_url} {folder}", shell=True)
                    print(f"Mirror selesai di {folder}")
            return None
        else:
            print("Password salah!")
            return None

    # Proot-distro versi smooth
    if b.lower() == "linux":
        result = subprocess.getoutput("proot-distro list")
        lines = result.splitlines()
        print("Distro tersedia:")
        distro_status = {}
        for line in lines:
            line = line.strip()
            if line.startswith("*"):
                name = line[1:].strip()
                print(f"{name} (installed)")
                distro_status[name] = True
            elif line:
                print(line)
                distro_status[line] = False

        distro = input("Pilih distro: ").strip()
        if distro:
            if not distro_status.get(distro, False):
                print(f"Distro {distro} belum terinstall. Menginstall sekarang...")
                subprocess.run(f"proot-distro install {distro}", shell=True)
                print(f"{distro} selesai diinstall!")
            print(f"Login ke {distro} ...")
            subprocess.run(f"proot-distro login {distro}", shell=True)
        return None

    # Plugin system
    if b.startswith("plugin"):
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
                    print(f"Mengaktifkan plugin {plugins[int(choice)-1]} ...")
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
                print(f"Download dari {url} ke {out_file} ...")
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

    # ----------------------------
    # CD command safe
    # ----------------------------
    if b.startswith("cd "):
        folder = b[3:].strip()
        if folder == "/":
            current_folder = "."  # aman ke root REPL
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

    # File explorer mini
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
        out_file = os.path.join(downloads_folder, filename)
        print(f"Download {url} ke {out_file} ...")
        subprocess.run(f"curl -o {out_file} {url}", shell=True)
        return None

    # Git download
    if b.startswith("git "):
        repo_url = b[4:].strip()
        repo_name = repo_url.split("/")[-1].replace(".git","")
        out_dir = os.path.join(downloads_folder, repo_name)
        print(f"Cloning {repo_url} ke {out_dir} ...")
        subprocess.run(f"git clone {repo_url} {out_dir}", shell=True)
        return None

    # Wget
    if b.startswith("wget "):
        url = b[5:].strip()
        filename = url.split("/")[-1]
        out_file = os.path.join(downloads_folder, filename)
        print(f"Download {url} ke {out_file} ...")
        subprocess.run(f"wget -O {out_file} {url}", shell=True)
        return None

    # Pindah file
    if b.startswith("pindah "):
        parts = b.split()
        if len(parts) < 3:
            print("Format: pindah <nama_file> <folder_tujuan>")
            return None
        file_name = parts[1]
        tujuan = parts[2]
        src_path = os.path.join(downloads_folder, file_name)
        if not os.path.exists(src_path):
            print(f"File {file_name} tidak ditemukan di downloads/")
            return None
        os.makedirs(tujuan, exist_ok=True)
        dst_path = os.path.join(tujuan, file_name)
        try:
            os.rename(src_path, dst_path)
            print(f"{file_name} berhasil dipindah ke {tujuan}/")
        except Exception as e:
            print("Gagal memindahkan file:", e)
        return None

    # ----------------------------
    # Command baru: simpan (backup)
    # ----------------------------
    if b.strip() == "simpan":
        backup_folder = "./backup"
        os.makedirs(backup_folder, exist_ok=True)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        target = os.path.join(backup_folder, f"backup_{timestamp}")
        os.makedirs(target, exist_ok=True)
        
        for folder in [downloads_folder, plugins_folder]:
            if os.path.exists(folder):
                subprocess.run(f"rsync -a {folder} {target}/", shell=True)
        if os.path.exists(session_file):
            subprocess.run(f"cp {session_file} {target}/", shell=True)
        print(f"Backup selesai! Tersimpan di {target}")
        return None

    # ----------------------------
    # Command baru: root -a
    # ----------------------------
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
        print("Proot-distro: linux")
        print("File/Network: ls, cat, ping, curl, wget, git")
        print("Plugin: plugin, plugin -m")
        print("File management: pindah <nama_file> <folder_tujuan>")
        print("Backup: simpan")
        print("Root mode: root -a")
        print("Change folder: cd <folder>, cd .. (naik 1 level), cd / (root REPL), keluar_folder (shortcut ke root)")
        return None

    # Semua command Linux lain
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
    print("\n=== Ultimate Bahasa Lo REPL Final v5 ===")
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
