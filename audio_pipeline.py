"""
audio_pipeline.py
=================
Ekstraksi fitur audio untuk mendeteksi apakah suara adalah AI atau asli manusia.

Fitur yang diekstrak:
  - MFCC (Mel-Frequency Cepstral Coefficients) -> ciri vokal/suara
  - Pitch (F0) dan statistiknya -> kerataan pitch AI vs variasi manusia
  - Spectral features -> centroid, bandwidth, rolloff, contrast
  - Zero Crossing Rate -> kehalusan sinyal AI
  - RMS Energy -> dinamika volume
  - Harmonic-to-Noise Ratio (HNR) -> kebersihan suara AI
  - Jitter & Shimmer (variasi pitch/amplitudo) -> ciri khas suara manusia

Penggunaan:
  python audio_pipeline.py --file suara.wav
  python audio_pipeline.py --real dataset/real_voice --ai dataset/ai_voice --duration 30
"""

import os
import sys
import io
import csv
import argparse
import warnings
import numpy as np

# Pastikan console Windows mendukung output UTF-8 (mencegah charmap error)
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True)

warnings.filterwarnings("ignore")

import librosa
import soundfile as sf

# ─────────────────────────────────────────────
# FUNGSI UTAMA: EKSTRAKSI FITUR
# ─────────────────────────────────────────────

def extract_features(file_path: str, sr: int = 22050, duration: float = 30.0) -> dict:
    """
    Ekstrak semua fitur audio dari satu file .wav / .mp3 / .ogg / .flac / .webm.

    Parameters
    ----------
    file_path : str   -> path ke file audio
    sr        : int   -> sample rate target (default 22050 Hz)
    duration  : float -> potong audio maksimal (detik), default 30 detik agar cepat dan akurat

    Returns
    -------
    dict berisi ~50 fitur numerik
    """
    try:
        y, sr = librosa.load(file_path, sr=sr, duration=duration, mono=True)
    except Exception as e:
        print(f"[ERROR] Gagal memuat audio {file_path}: {e}")
        return None

    if len(y) == 0:
        print(f"[WARN] Audio kosong: {file_path}")
        return None

    features = {"file": os.path.basename(file_path)}

    # ── 1. MFCC (13 koefisien) ──────────────────────────────────────────────
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    for i, coef in enumerate(mfcc):
        features[f"mfcc_{i+1}_mean"] = float(np.mean(coef))
        features[f"mfcc_{i+1}_std"]  = float(np.std(coef))

    # ── 2. DELTA MFCC (perubahan antar frame) ──────────────────────────────
    delta_mfcc = librosa.feature.delta(mfcc)
    for i, coef in enumerate(delta_mfcc):
        features[f"delta_mfcc_{i+1}_mean"] = float(np.mean(coef))

    # ── 3. PITCH (F0) ───────────────────────────────────────────────────────
    try:
        f0, voiced_flag, voiced_prob = librosa.pyin(
            y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"),
            sr=sr, frame_length=2048
        )
        f0_voiced = f0[~np.isnan(f0)] if f0 is not None else np.array([0.0])
    except Exception:
        f0_voiced = np.array([0.0])
        voiced_flag = np.array([False])

    features["pitch_mean"]   = float(np.mean(f0_voiced)) if len(f0_voiced) > 0 else 0.0
    features["pitch_std"]    = float(np.std(f0_voiced))  if len(f0_voiced) > 0 else 0.0
    features["pitch_min"]    = float(np.min(f0_voiced))  if len(f0_voiced) > 0 else 0.0
    features["pitch_max"]    = float(np.max(f0_voiced))  if len(f0_voiced) > 0 else 0.0
    features["pitch_range"]  = features["pitch_max"] - features["pitch_min"]
    features["voiced_ratio"] = float(np.mean(voiced_flag)) if voiced_flag is not None and len(voiced_flag) > 0 else 0.0

    # ── 4. SPECTRAL FEATURES ────────────────────────────────────────────────
    spec_centroid  = librosa.feature.spectral_centroid(y=y, sr=sr)
    spec_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    spec_rolloff   = librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.85)
    spec_flatness  = librosa.feature.spectral_flatness(y=y)
    spec_contrast  = librosa.feature.spectral_contrast(y=y, sr=sr, n_bands=6)

    features["spec_centroid_mean"]  = float(np.mean(spec_centroid))
    features["spec_centroid_std"]   = float(np.std(spec_centroid))
    features["spec_bandwidth_mean"] = float(np.mean(spec_bandwidth))
    features["spec_bandwidth_std"]  = float(np.std(spec_bandwidth))
    features["spec_rolloff_mean"]   = float(np.mean(spec_rolloff))
    features["spec_flatness_mean"]  = float(np.mean(spec_flatness))
    for i in range(spec_contrast.shape[0]):
        features[f"spec_contrast_{i}_mean"] = float(np.mean(spec_contrast[i]))

    # ── 5. CHROMA ───────────────────────────────────────────────────────────
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    features["chroma_mean"] = float(np.mean(chroma))
    features["chroma_std"]  = float(np.std(chroma))

    # ── 6. ZERO CROSSING RATE ────────────────────────────────────────────────
    zcr = librosa.feature.zero_crossing_rate(y)
    features["zcr_mean"] = float(np.mean(zcr))
    features["zcr_std"]  = float(np.std(zcr))

    # ── 7. RMS ENERGY ────────────────────────────────────────────────────────
    rms = librosa.feature.rms(y=y)
    features["rms_mean"] = float(np.mean(rms))
    features["rms_std"]  = float(np.std(rms))

    # ── 8. HARMONIC / PERCUSSIVE ─────────────────────────────────────────────
    y_harmonic, y_percussive = librosa.effects.hpss(y)
    features["harmonic_mean"]   = float(np.mean(np.abs(y_harmonic)))
    features["percussive_mean"] = float(np.mean(np.abs(y_percussive)))
    hnr = np.mean(np.abs(y_harmonic)) / (np.mean(np.abs(y_percussive)) + 1e-8)
    features["hnr"] = float(hnr)

    # ── 9. TEMPO ────────────────────────────────────────────────────────────
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    features["tempo"] = float(np.asarray(tempo).item() if np.ndim(tempo) > 0 else tempo)

    # ── 10. JITTER (variasi pitch frame ke frame) ────────────────────────────
    if len(f0_voiced) > 2:
        jitter = np.mean(np.abs(np.diff(f0_voiced))) / (np.mean(f0_voiced) + 1e-8)
        features["jitter"] = float(jitter)
    else:
        features["jitter"] = 0.0

    # ── 11. SHIMMER (variasi amplitudo) ─────────────────────────────────────
    frames = librosa.util.frame(y, frame_length=1024, hop_length=256)
    amp_per_frame = np.max(np.abs(frames), axis=0)
    if len(amp_per_frame) > 2:
        shimmer = np.mean(np.abs(np.diff(amp_per_frame))) / (np.mean(amp_per_frame) + 1e-8)
        features["shimmer"] = float(shimmer)
    else:
        features["shimmer"] = 0.0

    # ── 12. DURASI ──────────────────────────────────────────────────────────
    features["duration_sec"] = float(librosa.get_duration(y=y, sr=sr))

    return features


# ─────────────────────────────────────────────
# BATCH: PROSES SELURUH FOLDER
# ─────────────────────────────────────────────

def process_folder(folder_path: str, label: str, max_files: int = None, duration: float = 30.0) -> list:
    """
    Proses semua file audio di folder, tambahkan label.
    label: 'human' atau 'ai'
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
        return []

    supported = (".wav", ".mp3", ".ogg", ".flac", ".m4a", ".webm")
    files = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith(supported)
    ]
    if max_files:
        files = files[:max_files]

    results = []
    for i, fname in enumerate(files, 1):
        fpath = os.path.join(folder_path, fname)
        print(f"  [{i}/{len(files)}] Memproses: {fname} ...", flush=True)
        feats = extract_features(fpath, duration=duration)
        if feats:
            feats["label"] = label
            results.append(feats)
    return results


def build_features_csv(real_folder: str, ai_folder: str, output_csv: str = "features.csv", duration: float = 30.0):
    """
    Buat features.csv dari dua folder: real_voice & ai_voice.
    Menggunakan library bawaan csv (tanpa ketergantungan pandas).
    """
    print(f"\n📂 Memproses suara MANUSIA dari: {real_folder} (durasi: {duration}s/file)", flush=True)
    human_data = process_folder(real_folder, label="human", duration=duration)
    print(f"   ✓ Selesai: {len(human_data)} file suara manusia.", flush=True)

    print(f"\n📂 Memproses suara AI dari: {ai_folder} (durasi: {duration}s/file)", flush=True)
    ai_data = process_folder(ai_folder, label="ai", duration=duration)
    print(f"   ✓ Selesai: {len(ai_data)} file suara AI.", flush=True)

    all_data = human_data + ai_data
    if not all_data:
        print("\n[!] Belum ada file audio yang ditemukan di folder dataset.")
        print(f"    1. Masukkan file audio suara asli (.wav/.mp3) ke: {real_folder}")
        print(f"    2. Masukkan file audio suara AI (.wav/.mp3) ke: {ai_folder}")
        print("    Lalu jalankan kembali: python audio_pipeline.py\n", flush=True)
        return None

    # Tentukan urutan kolom header
    sample = all_data[0]
    fieldnames = ["file"] + [k for k in sample.keys() if k not in ("file", "label")] + ["label"]

    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_data)

    print(f"\n✅ Fitur tersimpan di: {output_csv}", flush=True)
    print(f"   Total sampel: {len(all_data)} ({len(human_data)} human, {len(ai_data)} AI)\n", flush=True)
    return all_data


# ─────────────────────────────────────────────
# MAIN CLI
# ─────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ekstraksi fitur audio AI Detector (GuardiVoice)")
    parser.add_argument("--file",     type=str, help="Ekstrak fitur satu file")
    parser.add_argument("--real",     type=str, default="dataset/real_voice", help="Folder suara manusia")
    parser.add_argument("--ai",       type=str, default="dataset/ai_voice",   help="Folder suara AI")
    parser.add_argument("--output",   type=str, default="features.csv",       help="Output CSV")
    parser.add_argument("--duration", type=float, default=30.0,               help="Durasi audio yang dianalisis per file (detik)")
    args = parser.parse_args()

    if args.file:
        feats = extract_features(args.file, duration=args.duration)
        if feats:
            print("\nFitur audio yang berhasil diekstrak:")
            for k, v in feats.items():
                print(f"  {k:35s}: {v}")

            # Evaluasi langsung dengan Algoritma BAMBS jika konfigurasi tersedia
            try:
                from bambs_algorithm import BAMBSDetector
                rules_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "detector_rules.json")
                if os.path.exists(rules_file):
                    det = BAMBSDetector.load_json(rules_file)
                    res = det.predict(feats)
                    print("\n" + "="*60)
                    print(f"  HASIL ANALISIS BAMBS: {res['verdict']} (Keyakinan: {res['confidence']}%)")
                    print("="*60)
                    for fid, b in res["boundaries"].items():
                        print(f"  • {b['name']}:")
                        print(f"      Nilai: {b['value']} {b['unit']} | Batas θ: {b['threshold']} | Status: {b['status']}")
                        print(f"      Diagnosa: {b['explanation']}")
                    print("="*60)
            except Exception as e:
                pass
    else:
        build_features_csv(args.real, args.ai, args.output, duration=args.duration)
