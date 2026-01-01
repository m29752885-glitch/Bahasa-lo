# main.py - Versi FINAL Bahasa-lo
import os
import sys
import subprocess
from config.pkg_config import (
    DOWNLOADS_FOLDER,
    PACKAGES_FOLDER,
    ADMIN_FOLDER,
    BACKUP_FOLDER,
    PLUGINS_FOLDER,
    progress_bar,
    LOADING_MSGS
)
from plugin_loader import auto_reload_all, activate_single_plugin, list_plugins, loaded_plugins
from blo_repl import repl_blo
from internal.int_mod_loader import load_internal_modules

# ===============================
# Globals
# ===============================
CURRENT_PATH = os.getcwd()
LEVEL_USER = "user"
LEVEL_ROOT = "root"
LEVEL_ADMIN = "admin"
user_level = LEVEL_USER

# ===============================
# Prompt
# ===============================
def get_prompt():
    if user_level == LEVEL_USER:
        return "(+)> "
    elif user_level == LEVEL_ROOT:
        return "[#]> "
    elif user_level == LEVEL_ADMIN:
        return "{+}> "
    return "> "

# ===============================
# Fungsi Bantuan
# ===============================
def menu_bantuan():
    print("""
=== Bantuan Bahasa-lo ===
- cd [folder]        : pindah folder
- ls                 : daftar file/folder
- buat file [nama]   : buat file baru
- buat folder [nama] : buat folder baru
- hapus [nama]       : hapus file/folder
- edit [nama]        : edit file dengan nano
- jalankan [file.blo]: jalankan file .blo
- linux              : masuk ke proot-distro (root/admin)
- plugin -i [plugin] : aktifkan plugin manual
- keluar             : keluar dari REPL
""")

# ===============================
# Fungsi Linux (proot-distro)
# ===============================
def masuk_linux():
    global user_level
    if user_level not in [LEVEL_ROOT, LEVEL_ADMIN]:
        print("❌ Hanya root/admin yang bisa masuk Linux")
        return

    try:
        # tampilkan list distro
        proses = subprocess.run(["proot-distro list"], capture_output=True, text=True)
        print(proses.stdout)
        distro = input("Pilih distro untuk login: ").strip()
        # login
        os.system(f"proot-distro login {distro} --shared-tmp")
    except Exception as e:
        print("❌ Error saat masuk Linux:", e)

# ===============================
# Fungsi File Explorer
# ===============================
def command_cd(args):
    global CURRENT_PATH
    if not args:
        print("❌ Masukkan nama folder")
        return
    folder = args[0]
    target = os.path.join(CURRENT_PATH, folder)
    if os.path.isdir(target):
        CURRENT_PATH = os.path.abspath(target)
        os.chdir(CURRENT_PATH)
    else:
        print("❌ Folder tidak ditemukan")

def command_ls(args):
    files = os.listdir(CURRENT_PATH)
    for f in files:
        print(f)

def command_buat_file(args):
    if not args:
        print("❌ Masukkan nama file")
        return
    nama_file = args[0]
    path_file = os.path.join(CURRENT_PATH, nama_file)
    with open(path_file, "w") as f:
        f.write("")
    print(f"✅ File dibuat: {path_file}")

def command_buat_folder(args):
    if not args:
        print("❌ Masukkan nama folder")
        return
    nama_folder = args[0]
    path_folder = os.path.join(CURRENT_PATH, nama_folder)
    os.makedirs(path_folder, exist_ok=True)
    print(f"✅ Folder dibuat: {path_folder}")

def command_hapus(args):
    if not args:
        print("❌ Masukkan nama file/folder")
        return
    nama = args[0]
    path = os.path.join(CURRENT_PATH, nama)
    if os.path.isfile(path):
        os.remove(path)
        print(f"✅ File dihapus: {path}")
    elif os.path.isdir(path):
        os.rmdir(path)
        print(f"✅ Folder dihapus: {path}")
    else:
        print("❌ File/folder tidak ditemukan")

def command_edit(args):
    if not args:
        print("❌ Masukkan nama file")
        return
    path_file = os.path.join(CURRENT_PATH, args[0])
    if os.path.exists(path_file):
        os.system(f"nano {path_file}")
    else:
        print("❌ File tidak ditemukan")

# ===============================
# Fungsi Jalankan .blo
# ===============================
def command_jalankan(args):
    if not args:
        print("❌ Masukkan file .blo")
        return
    path_file = os.path.join(CURRENT_PATH, args[0])
    if os.path.exists(path_file):
        repl_blo_file(path_file)
    else:
        print("❌ File tidak ditemukan")

def repl_blo_file(path_file):
    try:
        from blo_interpreter import jalankan_blo
        jalankan_blo(path_file)
    except Exception as e:
        print("❌ Error saat menjalankan .blo:", e)

# ===============================
# Fungsi Admin
# ===============================
def login_admin():
    global user_level
    password = input("Masukkan password admin: ")
    if password == "12345":
        user_level = LEVEL_ADMIN
        print("✅ Login admin berhasil")
    else:
        print("❌ Password salah")

# ===============================
# Fungsi Plugin
# ===============================
def plugin_manual(args):
    if not args:
        print("❌ Masukkan nama plugin")
        return
    plugin_name = args[0]
    activate_single_plugin(plugin_name)

# ===============================
# REPL Utama
# ===============================
KONTEKS = {
    "cwd": os.getcwd()
}

load_internal_modules(KONTEKS)

def repl():
    auto_reload_all()
    print("=== Bahasa-lo REPL FINAL ===")
    print(f"Level: {user_level}")

    while True:
        try:
            baris = input(get_prompt()).strip()
            if not baris:
                continue

            parts = baris.split()
            cmd = parts[0]
            args = parts[1:]

            # exit
            if cmd in ["keluar", "exit"]:
                print("Keluar dari Bahasa-lo REPL")
                break

            # bantuan
            elif cmd in ["bantuan", "help"]:
                menu_bantuan()

            # plugin manual
            elif cmd == "plugin" and len(args) >= 1:
                if args[0] == "-i" and len(args) >= 2:
                  plugin_manual(args[1:])
                elif args[0] == "-l":
                  list_plugins()
                else:
                  print("❌ Gunakan: plugin -i namaplugin ATAU plugin -l")

            # cd
            elif cmd == "cd":
                command_cd(args)

            # ls
            elif cmd == "ls":
                command_ls(args)

            # buat file
            elif cmd == "buat" and len(args) >= 2 and args[0] == "file":
                command_buat_file(args[1:])

            # buat folder
            elif cmd == "buat" and len(args) >= 2 and args[0] == "folder":
                command_buat_folder(args[1:])

            # hapus
            elif cmd == "hapus":
                command_hapus(args)

            # edit
            elif cmd == "edit":
                command_edit(args)

            # jalankan .blo
            elif cmd == "jalankan":
                command_jalankan(args)

            # linux
            elif cmd == "linux":
                masuk_linux()

            # login admin
            elif cmd == "admin":
                login_admin()

            # plugin manual
            elif cmd == "plugin" and len(args) >= 2 and args[0] == "-i":
                plugin_manual(args[1:])

            else:
                print("❌ Command tidak ditemukan")

        except KeyboardInterrupt:
            print("\nKeluar dari REPL")
            break
        except Exception as e:
            print("❌ Error:", e)

# ===============================
# Jalankan REPL
# ===============================
if __name__ == "__main__":
    repl()
      
