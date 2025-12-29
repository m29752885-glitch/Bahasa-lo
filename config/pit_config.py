# config/pit_config.py

# ----------------------------
# Repo list Termux
# Format tiap item:
# "nama_package | url_package | arch | tipe_repo"
# tipe_repo: termux
# ----------------------------
repo_list = [
    "nano | https://packages.termux.org/apt/termux-main/pool/main/n/nano/nano_6.4-1_all.deb | all | termux",
    "git | https://packages.termux.org/apt/termux-main/pool/main/g/git/git_2.41.0-1_aarch64.deb | arm64 | termux",
    "curl | https://packages.termux.org/apt/termux-main/pool/main/c/curl/curl_7.85.0-1_aarch64.deb | arm64 | termux",
    "htop | https://packages.termux.org/apt/termux-main/pool/universe/h/htop/htop_3.1.2-3_all.deb | all | termux",
    "python | https://packages.termux.org/apt/termux-main/pool/main/p/python/python_3.12.0-1_aarch64.deb | arm64 | termux",
]

# ----------------------------
# Mirror fallback Termux
# Gunanya: kalau URL utama gagal, coba mirror lain
# ----------------------------
mirrors = [
    "https://packages.termux.org/apt/termux-main/",
    # Bisa ditambah mirror lain
]

# ----------------------------
# Arsitektur target
# Biasanya arm64 di Termux
# ----------------------------
arch = "arm64"

# ----------------------------
# Folder tempat menyimpan hasil install pit
# ----------------------------
packages_folder = "./packages"

# ----------------------------
# Folder untuk log pit installer
# ----------------------------
log_file = "./packages/pit.log"
