"""
metadata_template.py
=====================
Script helper untuk membuat metadata.csv dari folder dataset kamu.
Jalankan ini SEBELUM audio_pipeline.py untuk membuat file metadata.

Penggunaan:
  python metadata_template.py
"""

import os
import csv

DATASET_DIR = "dataset"
OUTPUT_CSV  = "metadata.csv"

FOLDERS = {
    "real_voice": "human",
    "ai_voice":   "ai",
}

SUPPORTED = (".wav", ".mp3", ".ogg", ".flac", ".m4a")

rows = []
for folder, label in FOLDERS.items():
    folder_path = os.path.join(DATASET_DIR, folder)
    if not os.path.isdir(folder_path):
        print(f"[!] Folder tidak ada: {folder_path} — skip")
        continue

    files = [f for f in os.listdir(folder_path) if f.lower().endswith(SUPPORTED)]
    print(f"  {folder}: {len(files)} file ditemukan")
    for f in files:
        rows.append({
            "filename": f,
            "path":     os.path.join(folder_path, f),
            "label":    label,
            "source":   "",     # ← isi sumber suara (opsional), mis: "ElevenLabs", "Rekaman Sendiri"
            "notes":    "",     # ← catatan tambahan (opsional)
        })

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["filename", "path", "label", "source", "notes"])
    writer.writeheader()
    writer.writerows(rows)

print(f"\n✅ Metadata tersimpan: {OUTPUT_CSV} ({len(rows)} entri)")
print("   Buka file ini dan isi kolom 'source' dan 'notes' jika perlu.")
