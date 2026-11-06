# Panduan Lengkap: AI Detector Suara
## Proyek Deteksi Suara AI vs Manusia — IYSA 2025

---

## 📁 Struktur Folder Proyek

```
ai-detector-suara/
│
├── dataset/
│   ├── real_voice/          ← 📥 MASUKKAN SUARA MANUSIA DI SINI
│   └── ai_voice/            ← 📥 MASUKKAN SUARA AI DI SINI
│
├── models/                  ← model tersimpan otomatis setelah training
│   ├── detector.pkl
│   ├── confusion_matrix.png
│   ├── roc_curve.png
│   └── feature_importance.png
│
├── www/                     ← website frontend
│   ├── index.html
│   ├── css/style.css
│   └── js/api.js
│
├── audio_pipeline.py        ← ekstraksi fitur audio
├── train_model.py           ← training model ML
├── main.py                  ← API server FastAPI
├── metadata_template.py     ← helper buat metadata
└── requirements.txt         ← daftar library
```

---

## 🚀 LANGKAH 1 — Install Python & Library

```powershell
# Pastikan Python 3.10+ terinstall
python --version

# Buat virtual environment
python -m venv venv

# Aktifkan venv (Windows)
venv\Scripts\activate

# Install semua library
pip install -r requirements.txt
```

> **Jika pip diblokir (Application Control Policy):**  
> Buka PowerShell sebagai Administrator, jalankan:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
> pip install -r requirements.txt
> ```

---

## 📥 LANGKAH 2 — Masukkan Data Suara

### Format yang diterima:
| Format | Keterangan |
|--------|-----------|
| `.wav` | ✅ Paling direkomendasikan |
| `.mp3` | ✅ Oke |
| `.ogg` | ✅ Oke |
| `.flac`| ✅ Oke |
| `.m4a` | ✅ Oke |

### Cara memasukkan data:

**Suara Manusia Asli** → copy ke folder:
```
dataset/real_voice/
```
Contoh file:
- `rekaman_pak_budi.wav`
- `suara_presenter_tv.mp3`
- `wawancara_001.wav`

**Suara AI / TTS** → copy ke folder:
```
dataset/ai_voice/
```
Contoh file:
- `elevenlabs_output.mp3`
- `tts_google_001.wav`
- `ai_generated_speech.ogg`

### Rekomendasi jumlah data:
| Kategori | Minimum | Ideal |
|----------|---------|-------|
| Suara Manusia | 30 file | 100+ file |
| Suara AI | 30 file | 100+ file |

### Cara dapatkan data suara AI (gratis):
- **ElevenLabs** → elevenlabs.io (free tier 10.000 karakter/bulan)
- **Google TTS** → cloud.google.com/text-to-speech
- **Murf.ai** → murf.ai
- **Uberduck** → uberduck.ai
- **Coqui TTS** → install lokal, generate sendiri

---

## ⚙️ LANGKAH 3 — Ekstraksi Fitur

```powershell
# Masuk ke folder proyek
cd "C:\Jasim\BKI\ai detection\ai-detector-suara"

# Aktifkan venv
venv\Scripts\activate

# Ekstrak fitur dari semua file di dataset/
python audio_pipeline.py

# Output: features.csv akan terbuat otomatis
```

**Cek satu file saja (untuk test):**
```powershell
python audio_pipeline.py --file "dataset/real_voice/rekaman.wav"
```

---

## 🤖 LANGKAH 4 — Training & Kalibrasi Algoritma BAMBS

```powershell
python train_model.py
```

Algoritma BAMBS (*Bio-Acoustic Multi-Boundary Scoring*) akan otomatis:
1. Membaca `features.csv`
2. Mengkalibrasi 4 batasan fisik bio-akustik utama:
   - **`pitch_range`**: Rentang Dinamika Nada (Intonasi Biologis)
   - **`shimmer`**: Perturbasi Mikro-Amplitudo (Fluktuasi Getaran Glotis)
   - **`hnr`**: Harmonic-to-Noise Ratio (Resonansi Alami vs Residu)
   - **`mfcc_7_std`**: Dispersi Formant Spektral (Jejak Artifak Vocoder)
3. Melakukan Stratified 5-Fold Cross Validation
4. Menyimpan konfigurasi transparan ke `models/detector_rules.json` dan `models/detector.pkl`
5. Menghasilkan grafik: `confusion_matrix.png`, `roc_curve.png`, dan `boundaries_visualization.png`

**Hasil Evaluasi BAMBS:**
```
🔬 Validasi Silang (Stratified 5-Fold Cross Validation):
   Mean Accuracy : 1.0000 ± 0.0000
   Mean ROC-AUC  : 1.0000 ± 0.0000
   Mean F1-Score : 1.0000 ± 0.0000

📋 Ambang Batas (Decision Boundaries) Terkalibrasi:
   • Pitch Range : Ambang θ = 132.56 Hz (Bobot: 18.9%, Cohen's d: 1.55)
   • Shimmer     : Ambang θ = 0.1163    (Bobot: 21.7%, Cohen's d: 1.79)
   • HNR         : Ambang θ = 2.1655    (Bobot: 20.1%, Cohen's d: 1.65)
   • MFCC-7 Std  : Ambang θ = 14.4840   (Bobot: 39.3%, Cohen's d: 3.23)
```

---

## 🌐 LANGKAH 5 — Jalankan API Server

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Test API:**
```powershell
# Health check
curl http://localhost:8000/

# Info model
curl http://localhost:8000/info

# Prediksi file (gunakan PowerShell)
curl -X POST http://localhost:8000/predict `
  -F "file=@dataset/real_voice/rekaman.wav"
```

**Atau buka browser:**  
→ `http://localhost:8000/docs` (Swagger UI otomatis dari FastAPI)

---

## 🖥️ LANGKAH 6 — Buka Website Frontend

```powershell
# Cara 1: Python simple server
python -m http.server 3000 --directory www

# Cara 2: langsung buka index.html di browser
start www\index.html
```

Buka browser: `http://localhost:3000`

---

## 🔄 Alur Kerja Lengkap

```
Data Suara (WAV/MP3)
        ↓
dataset/real_voice/  ←── suara manusia
dataset/ai_voice/    ←── suara AI
        ↓
python audio_pipeline.py
        ↓
features.csv  (50+ fitur per file)
        ↓
python train_model.py
        ↓
models/detector.pkl  (model terlatih)
        ↓
uvicorn main:app --reload
        ↓
http://localhost:8000/predict  (API)
        ↓
www/index.html  (Website)
```

---

## 🧪 Fitur yang Diekstrak

| Fitur | Keterangan | AI vs Manusia |
|-------|-----------|---------------|
| **MFCC (13 koefisien)** | Sidik jari suara | Distribusi berbeda |
| **Pitch (F0)** | Frekuensi dasar | AI cenderung lebih stabil |
| **Jitter** | Variasi pitch antar-frame | Manusia lebih bervariasi |
| **Shimmer** | Variasi amplitudo | Manusia lebih tidak teratur |
| **HNR** | Harmonic-to-Noise Ratio | AI lebih tinggi (suara lebih "bersih") |
| **Spectral Centroid** | Kecerahan suara | Berbeda antara AI/manusia |
| **Zero Crossing Rate** | Kehalusan sinyal | AI cenderung lebih smooth |
| **Voiced Ratio** | Proporsi suara bersuara | AI lebih konsisten |

---

## ❓ Troubleshooting

### Error: `No module named 'librosa'`
```powershell
pip install librosa soundfile
```

### Error: `pip` diblokir
```powershell
# Jalankan sebagai Administrator
python -m pip install librosa soundfile --user
```

### Error: `Model belum ada`
```
Pastikan sudah jalankan:
1. python audio_pipeline.py   (buat features.csv)
2. python train_model.py      (buat models/detector.pkl)
```

### Error: `librosa.pyin` gagal / NaN
```
Normal untuk audio sangat pendek (< 1 detik).
Gunakan file audio minimal 3-5 detik.
```

### Website tidak konek ke API
```
Pastikan uvicorn sudah berjalan:
uvicorn main:app --reload
```

---

## 📊 Target Performa

| Metrik | Target Minimum | Target Ideal |
|--------|---------------|--------------|
| Accuracy | ≥ 85% | ≥ 95% |
| AUC-ROC | ≥ 0.90 | ≥ 0.97 |
| Precision | ≥ 85% | ≥ 95% |
| Recall | ≥ 85% | ≥ 95% |

> **Tips meningkatkan akurasi:**
> - Tambah lebih banyak data (≥ 200 file per kelas)
> - Pastikan kualitas audio setara (hindari noise berlebihan)
> - Gunakan berbagai sumber suara AI (bukan hanya satu TTS)

---

## 🔗 Referensi

- [librosa Documentation](https://librosa.org/doc/latest/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Scikit-learn Documentation](https://scikit-learn.org/)
- [Praat: Phonetics](https://www.fon.hum.uva.nl/praat/)
