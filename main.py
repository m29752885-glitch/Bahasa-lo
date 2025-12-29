# main.py
# Ultimate Bahasa Lo REPL Final – Admin & User Mode
import os, sys, subprocess, re, pickle, json, time
from config import pkg_config as cfg

# ----------------------------
# Setup folders dan config
# ----------------------------
os.makedirs(cfg.DOWNLOADS_FOLDER, exist_ok=True)
os.makedirs(cfg.PACKAGES_FOLDER, exist_ok=True)
os.makedirs(cfg.ADMIN_FOLDER, exist_ok=True)
os.makedirs(cfg.BACKUP_FOLDER, exist_ok=True)
os.makedirs(cfg.ADMIN_FOLDER+"/cloud", exist_ok=True)
os.makedirs(cfg.ADMIN_FOLDER+"/plugins", exist_ok=True)

# Load admin config
config_file = os.path.join(cfg.ADMIN_FOLDER,"config.json")
if os.path.exists(config_file):
    with open(config_file) as f:
        admin_config = json.load(f)
else:
    admin_config = {
        "password_admin":"12345",
        "prompt_admin":"[ADMIN]>",
        "allowed_folders":["downloads","packages","plugins","backup","admin/cloud"],
        "cloud_folder":"admin/cloud",
        "plugins_folder":"admin/plugins",
        "default_repo":[]
    }

# ----------------------------
# Variabel & alias bahasa Indonesia
# ----------------------------
variabel = {}
alias_perintah = {"Echo":"tulis"}
alias_keyword = {"jika":"if","apabila":"elif","Maka":":"}
macros = {}
session_file = ".session"
prompt_str = "(+)> "
current_folder = "."

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
# Logging
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
# File manager Linux vibe
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
    global current_folder, prompt_str

    b = b.strip()
    if b=="" or b.startswith("#"):
        return None

    # ----------------------------
    # Admin mode
    # ----------------------------
    if b.lower() == "admin":
        password = input("Masukkan password admin: ").strip()
        if password == admin_config["password_admin"]:
            print("Mode ADMIN aktif! Prompt:", admin_config["prompt_admin"])
            while True:
                baris_admin = input(admin_config["prompt_admin"]).strip()
                if baris_admin.lower() in ["keluar","exit"]:
                    print("Keluar dari admin mode.")
                    break
                # Admin commands
                if baris_admin == "tambah repo":
                    repo_url = input("Masukkan URL repo: ").strip()
                    repo_file = os.path.join(cfg.ADMIN_FOLDER,"repo.list")
                    os.makedirs(cfg.ADMIN_FOLDER, exist_ok=True)
                    with open(repo_file,"a") as f:
                        f.write(repo_url+"\n")
                    print(f"Repo berhasil ditambahkan di {repo_file}")
                elif baris_admin == "kelola fs":
                    while True:
                        print("\n--- FILE SYSTEM ADMIN ---")
                        print("1. Lihat isi folder")
                        print("2. Masuk folder (cd)")
                        print("3. Buat folder")
                        print("4. Hapus file/folder")
                        print("5. Lihat isi file")
                        print("6. Kembali ke prompt admin")
                        pilih = input("Pilih: ").strip()
                        if pilih=="1":
                            path = input("Path: ").strip() or "."
                            try:
                                for i in os.listdir(path):
                                    print(i)
                            except Exception as e:
                                print("Error:", e)
                        elif pilih=="2":
                            path = input("Folder: ").strip()
                            if os.path.isdir(path):
                                os.chdir(path)
                                print("Sekarang di:", os.getcwd())
                            else:
                                print("Folder tidak valid")
                        elif pilih=="3":
                            path = input("Nama folder baru: ").strip()
                            try:
                                os.makedirs(path, exist_ok=True)
                                print("Folder dibuat:", path)
                            except Exception as e:
                                print("Error:", e)
                        elif pilih=="4":
                            path = input("File/folder hapus: ").strip()
                            try:
                                if os.path.isdir(path):
                                    os.rmdir(path)
                                else:
                                    os.remove(path)
                                print("Berhasil dihapus")
                            except Exception as e:
                                print("Error:", e)
                        elif pilih=="5":
                            path = input("Nama file: ").strip()
                            try:
                                with open(path) as f:
                                    print(f.read())
                            except Exception as e:
                                print("Error:", e)
                        elif pilih=="6":
                            break
                else:
                    print("Perintah admin tidak dikenali.")
        else:
            print("Password salah! Akses ditolak.")
        return None

    # ----------------------------
    # Ganti alias perintah
    # ----------------------------
    for a in alias_perintah:
        if b.startswith(a+" "):
            b = b.replace(a, alias_perintah[a], 1)
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
    # Jalankan file .blo
    # ----------------------------
    if b.startswith("jalankan "):
        file = b[9:].strip()
        path_file = os.path.join(current_folder,file)
        if os.path.exists(path_file):
            with open(path_file) as f:
                kode = f.read().replace("jika","if").replace("apabila","elif").replace("Maka",":").replace("tulis","print")
            try:
                exec(kode, globals(), variabel)
            except Exception as e:
                print("Error:", e)
        else:
            print(f"File {file} tidak ditemukan!")
        return None

    # ----------------------------
    # File explorer
    # ----------------------------
    if b.startswith("ls"):
        folder = b[3:].strip() or current_folder
        list_files(folder)
        return None

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

    if b.startswith("cat "):
        file = os.path.join(current_folder, b[4:].strip())
        if os.path.exists(file):
            out = subprocess.getoutput(f"head -n 10 {file}")
            print(out)
            log(b,out)
        else:
            print(f"File '{file}' tidak ditemukan!")
        return None

    # ----------------------------
    # Plugin system
    # ----------------------------
    if b.startswith("plugin"):
        plugin_folder = os.path.join(cfg.ADMIN_FOLDER,"plugins")
        if b.strip() == "plugin -m":
            plugins = [f for f in os.listdir(plugin_folder) if f.endswith(".py")]
            if not plugins:
                print("Belum ada plugin.")
            else:
                print("Plugin tersedia:")
                for i,p in enumerate(plugins,1):
                    print(f"{i}. {p}")
                choice = input("Pilih plugin nomor: ").strip()
                if choice.isdigit() and 1<=int(choice)<=len(plugins):
                    try:
                        exec(open(os.path.join(plugin_folder,plugins[int(choice)-1])).read(),globals())
                        print("Plugin aktif!")
                    except Exception as e:
                        print("Gagal aktifkan plugin:",e)
            return None
        elif b.strip() == "plugin":
            print("Menu Plugin:")
            print("1. Buat file plugin sendiri")
            print("2. Upload dari GitHub")
            choice = input("Pilih opsi: ").strip()
            if choice=="1":
                filename = input("Nama file plugin (.py): ").strip()
                path = os.path.join(plugin_folder,filename)
                with open(path,"w") as f:
                    f.write("# Plugin baru\n")
                print(f"Plugin {filename} dibuat di {plugin_folder}")
            elif choice=="2":
                url = input("Masukkan URL plugin (.py): ").strip()
                out_file = os.path.join(plugin_folder,url.split("/")[-1])
                subprocess.run(f"wget -O {out_file} {url}", shell=True)
                print(f"Plugin tersimpan di {out_file}")
            return None

    # ----------------------------
    # Semua perintah Linux lainnya
    # ----------------------------
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
    print("\n=== Ultimate Bahasa Lo REPL Final ===")
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
