# int_mod_loader.py
# =========================
# Loader internal module (SILENT)
# =========================

import os
import importlib.util

INT_MOD_PATH = "./internal/int_mod"
loaded_int_mod = {}

def load_internal_modules(context=None):
    if not os.path.exists(INT_MOD_PATH):
        return

    for file in os.listdir(INT_MOD_PATH):
        if not file.endswith(".py") or file.startswith("_"):
            continue

        name = file[:-3]
        path = os.path.join(INT_MOD_PATH, file)

        try:
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            # inject context jika ada
            if hasattr(mod, "init"):
                mod.init(context)

            loaded_int_mod[name] = mod
        except Exception:
            pass  # SILENT (no output)
