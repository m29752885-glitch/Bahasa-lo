# plugin_advance.py
import os, pickle

PLUGINS_FOLDER = "./downloads/plugins"
PLUGIN_STATUS_FILE = os.path.join(PLUGINS_FOLDER, ".status.pkl")

# Load status plugin
if os.path.exists(PLUGIN_STATUS_FILE):
    with open(PLUGIN_STATUS_FILE, "rb") as f:
        plugin_status = pickle.load(f)
else:
    plugin_status = {}  # plugin: True/False

def simpan_status():
    with open(PLUGIN_STATUS_FILE, "wb") as f:
        pickle.dump(plugin_status, f)

def menu_plugin_controller():
    plugins = [f for f in os.listdir(PLUGINS_FOLDER) if f.endswith(".py") and f != "plugin_controller.py"]
    if not plugins:
        print("Belum ada plugin.")
        return

    while True:
        print("\n=== Menu Kontrol Plugin ===")
        for i, p in enumerate(plugins, 1):
            status = "Aktif" if plugin_status.get(p, True) else "Nonaktif"
            print(f"{i}. {p} [{status}]")
        print("0. Keluar menu")

        choice = input("Pilih plugin untuk toggle atau 0 untuk keluar: ").strip()
        if choice == "0":
            break
        if choice.isdigit() and 1 <= int(choice) <= len(plugins):
            plugin = plugins[int(choice)-1]
            plugin_status[plugin] = not plugin_status.get(plugin, True)
            print(f"{plugin} sekarang {'Aktif' if plugin_status[plugin] else 'Nonaktif'}")
            simpan_status()
        else:
            print("Pilihan tidak valid.")

# Auto reload plugin yang aktif
for file in os.listdir(PLUGINS_FOLDER):
    if file.endswith(".py") and file != "plugin_controller.py" and plugin_status.get(file, True):
        try:
            exec(open(os.path.join(PLUGINS_FOLDER, file)).read(), globals())
        except Exception as e:
            print(f"Gagal load {file}: {e}")
