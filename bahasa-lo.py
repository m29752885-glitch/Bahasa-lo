# Ultimate Bahasa Lo REPL + Pit Final v7
import os, sys, re, subprocess, pickle, time, gzip, urllib.request

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
required_packages = ["rsync","apt-mirror","git","wget","curl","proot-distro","gzip"]
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
packages_folder = "./packages"
plugins_folder = os.path.join(downloads_folder, "plugins")
repos_file = "./repo/repo.list"
os.makedirs(downloads_folder, exist_ok=True)
os.makedirs(plugins_folder, exist_ok=True)
os.makedirs(packages_folder, exist_ok=True)
os.makedirs(os.path.dirname(repos_file), exist_ok=True)
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
# Pit install helpers
# ----------------------------
def load_repos():
    repos = []
    if os.path.exists(repos_file):
        with open(repos_file,"r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    repos.append(line)
    return repos

def check_mirror(url):
    try:
        with urllib.request.urlopen(url) as resp:
            return resp.status == 200
    except:
        return False

def fetch_packages_gz(repo_url):
    packages_url = repo_url.rstrip("/") + "/dists/focal/universe/binary-amd64/Packages.gz"
    try:
        tmp_file = "/tmp/packages.gz"
        urllib.request.urlretrieve(packages_url, tmp_file)
        with gzip.open(tmp_file, 'rt') as f:
            return f.read()
    except:
        return ""

def pit_install(pkg):
    repos = load_repos()
    if not repos:
        print("Repo list kosong! Tambahkan repo di /repo/repo.list")
        return
    found = False
    print(f"Searching package '{pkg}' in repos...")
    for repo in repos:
        mirror_ok = check_mirror(repo)
        print(f"Testing available mirror: {repo} : {'ok' if mirror_ok else 'bad'}")
        if not mirror_ok:
            continue
        packages_text = fetch_packages_gz(repo)
        if not packages_text:
            continue
        # Cari paket
        pattern = re.compile(r'Package: '+re.escape(pkg)+r'.*?Filename: (.*?)\n', re.S)
        match = pattern.search(packages_text)
        if match:
            filename = match.group(1)
            url_pkg = repo.rstrip("/") + "/" + filename
            out_dir = os.path.join(packages_folder, pkg)
            os.makedirs(out_dir, exist_ok=True)
            out_file = os.path.join(out_dir, os.path.basename(filename))
            print(f"Downloading {url_pkg} -> {out_file} ...")
            try:
                urllib.request.urlretrieve(url_pkg, out_file)
                print(f"Package {pkg} berhasil di-download ke {out_file}")
                found = True
                break
            except Exception as e:
                print("Gagal download:", e)
    if not found:
        print(f"Paket {pkg} tidak ditemukan di semua repo.")

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
            print("1. Repo GitHub\n2. Repo Linux\n3. Edit repo pit")
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
            elif choice=="3":
                print("Isi repo saat ini:")
                repos = load_repos()
                for r in repos:
                    print(r)
                new = input("Tambah repo baru: ").strip()
                if new:
                    with open(repos_file,"a") as f:
                        f.write(new+"\n")
                    print("Repo ditambahkan!")
            return None

    # Pit commands
    if b.startswith("pit "):
        parts = b.split()
        if len(parts) >= 2:
            cmd = parts[1]
            if cmd == "install" and len(parts) == 3:
                pit_install(parts[2])
                return None
        print("Syntax pit: pit install <package> | pit search <package> | pit show <package>")
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

    # Jalankan file .blo
    if b.startswith("jalankan "):
        file_blo = os.path.join(current_folder, b[8:].strip())
        if os.path.exists(file_blo):
            with open(file_blo) as f:
                code = f.read()
                for k, v in alias_keyword.items():
                    code = re.sub(r'\b'+k+r'\b', v, code)
                exec(code, globals(), variabel)
        else:
            print("File .blo tidak ditemukan!")
        return None

    # File manager
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
    print("\n=== Ultimate Bahasa Lo REPL + Pit Final v7 ===")
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
