# plugin_loader.py
# ======================
# Load dan manage plugin Bahasa-lo
# ======================

import os
import importlib.util

PLUGINS_FOLDER = "./downloads/plugins"
loaded_plugins = {}  # plugin aktif

# ======================
# Auto reload plugin tertentu
# ======================
def auto_reload_all():
    global loaded_plugins
    plugin_list = ["Explorer_fix", "Optimasi", "crash_handle, Manual"]
    for plugin in plugin_list:
        path = os.path.join(PLUGINS_FOLDER, plugin + ".py")
        if os.path.exists(path):
            spec = importlib.util.spec_from_file_location(plugin, path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            loaded_plugins[plugin] = mod
        else:
            print(f"⚠️ Plugin {plugin} tidak ditemukan")

# ======================
# Aktifkan plugin manual
# ======================
def activate_single_plugin(plugin_name):
    global loaded_plugins
    path = os.path.join(PLUGINS_FOLDER, plugin_name + ".py")
    if os.path.exists(path):
        spec = importlib.util.spec_from_file_location(plugin_name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        loaded_plugins[plugin_name] = mod
        print(f"✅ Plugin {plugin_name} diaktifkan")
    else:
        print(f"❌ Plugin {plugin_name} tidak ditemukan")
