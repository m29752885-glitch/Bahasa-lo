# auto_reload.py
# Plugin: Selektif Auto-Reload
# Letak: ./downloads/plugins/

import os, json

CONFIG_FILE = "./downloads/plugins/auto_reload_config.json"
PLUGIN_FOLDER = "./downloads/plugins"

# Load config atau buat default
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
else:
    config = {
        "master_switch": True,  # True = semua auto-reload aktif
        "enabled_plugins": []   # list plugin yang auto-reload
    }

# Simpan config
def simpan_config():
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

# Tampilkan status
def status():
    tulis("=== Status Auto-Reload Plugin ===")
    tulis(f"Master Switch: {'ON' if config['master_switch'] else 'OFF'}")
    tulis("Plugin yang auto-reload:")
    if not config["enabled_plugins"]:
        tulis("  Tidak ada plugin terpilih")
    else:
        for p in config["enabled_plugins"]:
            tulis(f"  - {p}")

# Toggle master switch
def toggle_master():
    config["master_switch"] = not config["master_switch"]
    simpan_config()
    tulis(f"Master Switch sekarang: {'ON' if config['master_switch'] else 'OFF'}")

# Aktifkan plugin tertentu
def aktifkan(plugin_name):
    if plugin_name not in os.listdir(PLUGIN_FOLDER):
        tulis(f"Plugin '{plugin_name}' tidak ditemukan!")
        return
    if plugin_name not in config["enabled_plugins"]:
        config["enabled_plugins"].append(plugin_name)
        simpan_config()
        tulis(f"Plugin '{plugin_name}' diaktifkan untuk auto-reload")
    else:
        tulis(f"Plugin '{plugin_name}' sudah aktif")

# Nonaktifkan plugin tertentu
def nonaktifkan(plugin_name):
    if plugin_name in config["enabled_plugins"]:
        config["enabled_plugins"].remove(plugin_name)
        simpan_config()
        tulis(f"Plugin '{plugin_name}' dinonaktifkan untuk auto-reload")
    else:
        tulis(f"Plugin '{plugin_name}' sudah nonaktif")

# Menu utama plugin
def menu():
    tulis("=== Plugin Auto-Reload Menu ===")
    tulis("1. Toggle master switch")
    tulis("2. Aktifkan plugin tertentu")
    tulis("3. Nonaktifkan plugin tertentu")
    tulis("4. Lihat status")
    pilihan = masukan("Pilih opsi: ").strip()
    if pilihan == "1":
        toggle_master()
    elif pilihan == "2":
        p = masukan("Nama plugin: ").strip()
        aktifkan(p)
    elif pilihan == "3":
        p = masukan("Nama plugin: ").strip()
        nonaktifkan(p)
    elif pilihan == "4":
        status()
    else:
        tulis("Pilihan tidak valid")

# Auto-reload saat REPL load
def auto_reload(plugins_dict):
    if config["master_switch"]:
        for p in plugins_dict:
            if p in config["enabled_plugins"]:
                try:
                    exec(open(os.path.join(PLUGIN_FOLDER, p)).read(), globals())
                except Exception as e:
                    tulis(f"Gagal auto-reload {p}: {e}")
