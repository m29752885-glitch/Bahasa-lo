# agent_adaptive.py
# AI Adaptive Bahasa-lo (.blo)

import os
from info import INFO  # semua info sistem, plugin, command, panduan .blo
from blo_interpreter import translate_blo, jalankan_blo

# ==========================
# Agent State
# ==========================
class AgentAdaptive:
    def __init__(self):
        self.known_files = set()
        self.known_plugins = set()
        self.debug = True

    # ==========================
    # Deteksi file baru / .blo
    # ==========================
    def scan_files(self, folder="./downloads"):
        files = os.listdir(folder)
        new_files = [f for f in files if f not in self.known_files and f.endswith(".blo")]
        for nf in new_files:
            print(f"📌 File .blo baru terdeteksi: {nf}")
            self.known_files.add(nf)
        return new_files

    # ==========================
    # Berikan tips berdasarkan info.py
    # ==========================
    def advice(self, command):
        if command in INFO:
            print(f"💡 Tips untuk '{command}': {INFO[command]}")
        else:
            print(f"⚠️ Command '{command}' belum ada di info.py")

    # ==========================
    # Jalankan file .blo
    # ==========================
    def jalankan_blo(self, path):
        if os.path.exists(path):
            print(f"🚀 Menjalankan {path} ...")
            try:
                from blo_interpreter import jalankan_blo
                jalankan_blo(path, debug=self.debug)
            except Exception as e:
                print(f"❌ Error saat menjalankan {path}: {e}")
        else:
            print(f"❌ File {path} tidak ditemukan")

    # ==========================
    # Adaptive Loop
    # ==========================
    def interaktif(self):
        print("=== Agent Adaptive Bahasa-lo ===")
        print("Ketik 'keluar' untuk berhenti, 'scan' untuk cek file .blo baru, 'jalankan nama.blo' untuk run file .blo")
        while True:
            try:
                cmd = input("agent> ").strip()
                if cmd.lower() == "keluar":
                    print("🛑 Keluar dari Agent Adaptive")
                    break
                elif cmd.lower() == "scan":
                    self.scan_files()
                elif cmd.startswith("jalankan "):
                    path_file = cmd.split(" ", 1)[1]
                    self.jalankan_blo(path_file)
                else:
                    self.advice(cmd)
            except KeyboardInterrupt:
                print("\n🛑 Agent dihentikan")
                break

# ==========================
# Jalankan agent langsung
# ==========================
if __name__ == "__main__":
    agent = AgentAdaptive()
    agent.interaktif()
