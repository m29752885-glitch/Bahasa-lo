# pkg_config.py
# ----------------------------
# Konfigurasi folder dan progress system untuk REPL
# ----------------------------

import os

# ----------------------------
# Folder utama
# ----------------------------
DOWNLOADS_FOLDER = "./downloads" # file hasil download di luar proot-distro
PACKAGES_FOLDER = "./packages"   # file / package dari proot-distro
ADMIN_FOLDER = "./admin"
BACKUP_FOLDER = "./backup"
PLUGINS_FOLDER = os.path.join(DOWNLOADS_FOLDER, "plugins")  # folder plugin

# Pastikan semua folder ada
for folder in [DOWNLOADS_FOLDER, PACKAGES_FOLDER, ADMIN_FOLDER, BACKUP_FOLDER, PLUGINS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# ----------------------------
# Progress bar settings
# ----------------------------
PROGRESS_LENGTH = 20        # panjang bar
PROGRESS_SYMBOL = "█"       # simbol bar
PROGRESS_SPEED = 0.05       # jeda per langkah (detik)

# ----------------------------
# Loading message standar
# ----------------------------
LOADING_MSGS = {
    "download_file": "Mengunduh file...",
    "install_pkg": "Menginstall package...",
    "check_rootfs": "Memeriksa RootFS...",
    "install_rootfs": "Menginstall RootFS Ubuntu...",
    "login_rootfs": "Login ke RootFS...",
}

# ----------------------------
# Fungsi progress bar
# ----------------------------
def progress_bar(task_name, duration=1):
    """Menampilkan progress bar sederhana"""
    import sys, time
    print(f"{task_name} ", end="")
    sys.stdout.flush()
    for i in range(PROGRESS_LENGTH):
        print(PROGRESS_SYMBOL, end="")
        sys.stdout.flush()
        time.sleep(duration / PROGRESS_LENGTH)
    print(" Selesai!")
