# plugins/optimasi_system.py
import psutil

try:
    print(f"CPU     : {psutil.cpu_count()} cores | {psutil.cpu_percent()}% usage")
except PermissionError:
    print("CPU     : Tidak tersedia (izin terbatas)")

try:
    print(f"RAM     : {psutil.virtual_memory().percent}% used")
except PermissionError:
    print("RAM     : Tidak tersedia (izin terbatas)")

try:
    print(f"Disk    : {psutil.disk_usage('/').percent}% used")
except PermissionError:
    print("Disk    : Tidak tersedia (izin terbatas)")
