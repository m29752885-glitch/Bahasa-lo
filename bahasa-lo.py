# Ultimate REPL v11 – Full Final Script
import os, sys, re, time, pickle, subprocess, gzip, io, urllib.request

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
plugins_folder = os.path.join(downloads_folder,"plugins")
repos_file = "./repo/repo.list"
os.makedirs(downloads_folder, exist_ok=True)
os.makedirs(packages_folder, exist_ok=True)
os.makedirs(plugins_folder, exist_ok=True)
os.makedirs("./repo", exist_ok=True)
prompt_str = "(+)> "
current_folder = "."
repos = []

# ----------------------------
# Load repo.list
# ----------------------------
if os.path.exists(repos_file):
    with open(repos_file,"r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                repos.append(line)

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
# File manager versi Linux vibes
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
# Download file dengan progress
# ----------------------------
def download_with_progress(url, folder):
    filename = url.split("/")[-1]
    out_file = os.path.join(folder, filename)
    req = urllib.request.urlopen(url)
    total = int(req.getheader('Content-Length').strip())
    chunk_size = 8192
    downloaded = 0
    with open(out_file,"wb") as f:
        while True:
            chunk = req.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
            done = int(20*downloaded/total)
            sys.stdout.write("\r[" + "█"*done + " "*(20-done) + f"] {downloaded}/{total}B")
            sys.stdout.flush()
    print(f"\nSelesai: {out_file}")
    return out_file

# ----------------------------
# Parse Packages.gz dan cari paket
# ----------------------------
def parse_packages_gz(url):
    try:
        with urllib.request.urlopen(url) as response:
            compressed = response.read()
        with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as f:
            data = f.read().decode()
        entries = data.split("\n\n")
        pkgs = []
        for e in entries:
            pkg = {}
            for line in e.splitlines():
                if ":" in line:
                    k,v = line.split(":",1)
                    pkg[k.strip()] = v.strip()
            if "Package" in pkg and "Filename" in pkg:
                pkgs.append(pkg)
        return pkgs
    except Exception as ex:
        return []

# ----------------------------
# Pit install
# ----------------------------
def pit_install(paket):
    found = False
    for repo in repos:
        for comp in ["main","universe","multiverse","restricted"]:
            url = f"{repo}/dists/focal/{comp}/binary-arm64/Packages.gz"
            entries = parse_packages_gz(url)
            for e in entries:
                if e['Package'] == paket:
                    deb_url = repo + "/" + e['Filename']
                    folder = os.path.join(packages_folder,paket)
                    os.makedirs(folder, exist_ok=True)
                    print(f"Downloading {paket}...")
                    download_with_progress(deb_url, folder)
                    print(f"{paket} siap dipakai di {folder}")
                    found = True
                    break
            if found: break
        if found: break
    if not found:
        print(f"Paket {paket} tidak ditemukan di semua repo!")

# ----------------------------
# REPL: proses baris
# ----------------------------
def proses_baris(b):
    b = b.strip()
    if b=="" or b.startswith("#"):
        return None

    global current_folder, prompt_str

    # Ganti alias perintah
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

    # CD
    if b.startswith("cd "):
        folder = b[3:].strip()
        if folder=="..":
            current_folder = os.path.dirname(current_folder)
        else:
            target = os.path.join(current_folder, folder)
            if os.path.isdir(target):
                current_folder = os.path.abspath(target)
            else:
                print(f"Folder '{folder}' tidak ada!")
        return None

    # ls
    if b.startswith("ls"):
        folder = current_folder
        list_files(folder)
        return None

    # cat
    if b.startswith("cat "):
        file = os.path.join(current_folder, b[4:].strip())
        if os.path.exists(file):
            out = subprocess.getoutput(f"head -n 10 {file}")
            print(out)
        else:
            print(f"File '{file}' tidak ada!")
        return None

    # jalankan file .blo
    if b.startswith("jalankan "):
        fname = os.path.join(current_folder, b[8:].strip())
        if os.path.exists(fname):
            with open(fname,"r") as f:
                kode = f.read()
            try:
                # Replace keyword sesuai alias
                for a in alias_perintah:
                    kode = kode.replace(a,alias_perintah[a])
                for k in alias_keyword:
                    kode = re.sub(r'\b'+k+r'\b',alias_keyword[k],kode)
                exec(kode, globals(), variabel)
            except Exception as e:
                print("Error menjalankan file:", e)
        else:
            print(f"File {fname} tidak ada!")
        return None

    # pit commands
    if b.startswith("pit "):
        parts = b.split()
        cmd = parts[1]
        if cmd=="install" and len(parts)>2:
            pit_install(parts[2])
        elif cmd=="search" and len(parts)>2:
            print(f"Fungsi search paket {parts[2]} masih placeholder")
        elif cmd=="show" and len(parts)>2:
            print(f"Fungsi show paket {parts[2]} masih placeholder")
        else:
            print("Perintah pit tidak dikenali")
        return None

    # Linux command fallback
    try:
        subprocess.run(b, shell=True, cwd=current_folder)
    except:
        print("Terjadi kesalahan menjalankan:", b)
    return None

# ----------------------------
# REPL loop
# ----------------------------
def repl():
    global current_folder, prompt_str
    print("\n=== Ultimate Bahasa Lo REPL v11 ===")
    print("Ketik 'keluar' untuk keluar")
    while True:
        if current_folder==".":
            prompt = "[Root]> " if prompt_str.startswith("[Root]") else "(+)> "
        else:
            prompt = f"[Root]/{os.path.basename(current_folder)}> " if prompt_str.startswith("[Root]") else f"(+) / {os.path.basename(current_folder)}> "
        baris = input(prompt)
        if baris.lower() in ["keluar","exit"]:
            with open(session_file,"wb") as f:
                pickle.dump({"variabel":variabel,"macros":macros},f)
            print("Session tersimpan. Bye!")
            break
        proses_baris(baris)

if __name__=="__main__":
    repl()
