# main.py - Bahasa-lo FINAL
import os, shutil, subprocess, sys
from blo_interpreter import jalankan_blo
from plugin_loader import auto_reload_all, activate_single_plugin, PLUGINS_FOLDER

# -----------------------------
# Globals
# -----------------------------
LEVEL = "user"  # user, root, admin
CURRENT_DIR = os.getcwd()

# -----------------------------
# Fungsi bantu file/folder
# -----------------------------
def buat(path, jenis="file"):
    path = os.path.join(CURRENT_DIR, path)
    try:
        if jenis == "file":
            with open(path, "w") as f: pass
            print(f"✅ File {path} dibuat")
        elif jenis == "folder":
            os.makedirs(path, exist_ok=True)
            print(f"✅ Folder {path} dibuat")
    except Exception as e:
        print(f"❌ Gagal buat {jenis} {path}: {e}")

def hapus(path):
    path = os.path.join(CURRENT_DIR, path)
    if not os.path.exists(path):
        print(f"❌ {path} tidak ditemukan")
        return
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        print(f"✅ {path} berhasil dihapus")
    except Exception as e:
        print(f"❌ Gagal menghapus {path}: {e}")

def edit(path):
    path = os.path.join(CURRENT_DIR, path)
    if not os.path.exists(path):
        print(f"❌ {path} tidak ditemukan")
        return
    editor = os.environ.get("EDITOR","nano")
    subprocess.call([editor, path])

def masuk_admin():
    global LEVEL
    pwd = input("Masukkan password admin: ")
    if pwd == "12345":  # password default
        LEVEL = "admin"
        print("✅ Login admin berhasil")
    else:
        print("❌ Password salah")

# -----------------------------
# Fungsi Linux (termux/proot)
# -----------------------------
def masuk_linux():
    if LEVEL not in ["admin","root"]:
        print("❌ Hanya admin/root bisa masuk Linux")
        return
    # tampilkan list distro
    print("Menampilkan distro proot-distro...")
    subprocess.call(["proot-distro", "list"])
    nama = input("Pilih distro yang diinstall: ")
    print(f"Login ke {nama} ...")
    subprocess.call(["proot-distro", "login", nama])

# -----------------------------
# Fungsi REPL Bahasa-lo
# -----------------------------
def repl():
    global CURRENT_DIR
    print("=== Bahasa-lo REPL FINAL ===")
    while True:
        prompt = "(+)>" if LEVEL=="user" else "[#]>" if LEVEL=="root" else "{+}>"
        try:
            baris = input(prompt + " ").strip()
            if baris == "exit":
                break
            elif baris.startswith("cd "):
                target = baris[3:].strip()
                try:
                    os.chdir(target)
                    CURRENT_DIR = os.getcwd()
                except Exception as e:
                    print(f"❌ {e}")
            elif baris == "ls":
                print("\n".join(os.listdir(CURRENT_DIR)))
            elif baris.startswith("buat "):
                args = baris[5:].split()
                if len(args)==2 and args[0] in ["file","folder"]:
                    buat(args[1], args[0])
                else:
                    print("Format: buat file|folder nama")
            elif baris.startswith("hapus "):
                hapus(baris[6:].strip())
            elif baris.startswith("edit "):
                edit(baris[5:].strip())
            elif baris.startswith("jalankan "):
                path_file = baris[9:].strip()
                jalankan_blo(path_file)
            elif baris.startswith("plugin -i "):
                activate_single_plugin(baris[10:].strip())
            elif baris=="plugin -r":
                auto_reload_all()
            elif baris=="linux":
                masuk_linux()
            elif baris=="admin":
                masuk_admin()
            else:
                # coba eval Python biasa
                try: 
                    exec(baris)
                except Exception as e:
                    print(f"❌ Error: {e}")
        except KeyboardInterrupt:
            print("\nKeluar dari REPL")
            break

# -----------------------------
# Main
# -----------------------------
if __name__=="__main__":
    # Auto reload plugin tertentu
    auto_reload_all()
    repl()
