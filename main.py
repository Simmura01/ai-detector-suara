"""
main.py — FastAPI Backend (BAMBS Version)
=========================================
API server untuk deteksi suara AI vs Manusia menggunakan Algoritma BAMBS
(Bio-Acoustic Multi-Boundary Scoring) berbasis 4 batasan fisik akustik utama.

Jalankan:
  uvicorn main:app --reload --host 0.0.0.0 --port 8000

Endpoint:
  GET  /            → health check
  GET  /info        → info algoritma & 4 batasan
  POST /predict     → upload file audio, dapat prediksi + diagnosa batasan
  POST /predict-url → kirim URL audio (opsional)
"""

import os
import io
import uuid
import tempfile
import warnings
import traceback
import numpy as np
import joblib

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

warnings.filterwarnings("ignore")

# ── Import pipeline fitur & algoritma kustom ──────────────────────────────
from audio_pipeline import extract_features
from bambs_algorithm import BAMBSDetector, KEY_BOUNDARIES

# ── Inisialisasi FastAPI ──────────────────────────────────────────────────
app = FastAPI(
    title="AI Detector Suara API (BAMBS)",
    description="Deteksi suara AI vs Manusia berbasis 4 Batasan Fisik Akustik Transparan.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "detector.pkl")
RULES_PATH = os.path.join(BASE_DIR, "models", "detector_rules.json")

detector_instance = None
model_meta = None


@app.on_event("startup")
def load_model():
    global detector_instance, model_meta

    if os.path.exists(MODEL_PATH):
        try:
            model_meta = joblib.load(MODEL_PATH)
            detector_instance = model_meta.get("detector") or model_meta.get("model")
            print(f"✅ Model BAMBS dimuat dari {MODEL_PATH}")
            print(f"   Accuracy: {model_meta.get('test_accuracy', 'N/A')} | AUC: {model_meta.get('test_auc', 'N/A')}")
            return
        except Exception as e:
            print(f"⚠️ Gagal memuat pickle ({e}), mencoba load dari JSON rules...")

    if os.path.exists(RULES_PATH):
        detector_instance = BAMBSDetector.load_json(RULES_PATH)
        model_meta = {
            "model_name": "BAMBS (Bio-Acoustic Multi-Boundary Scoring)",
            "detector": detector_instance,
            "feature_names": detector_instance.feature_names,
            "test_accuracy": detector_instance.metrics.get("test_accuracy", 1.0),
            "test_auc": detector_instance.metrics.get("test_auc", 1.0),
        }
        print(f"✅ Model BAMBS dimuat dari {RULES_PATH}")
    else:
        print(f"⚠️ Model belum ditemukan di {MODEL_PATH} atau {RULES_PATH}")
        print("   Jalankan: python train_model.py")


# ─────────────────────────────────────────────
# HELPER: PREDIKSI DARI FEATURES DICT
# ─────────────────────────────────────────────

def predict_from_features(feats: dict) -> dict:
    if detector_instance is None:
        raise HTTPException(
            status_code=503,
            detail="Model BAMBS belum diload. Silakan jalankan 'python train_model.py' terlebih dahulu."
        )

    # Jalankan prediksi dengan Algoritma BAMBS
    result = detector_instance.predict(feats)

    # Sertakan summary fitur untuk kompatibilitas frontend
    result["features_summary"] = {
        "duration_sec":    round(float(feats.get("duration_sec", 0.0) or 0.0), 2),
        "pitch_mean_hz":   round(float(feats.get("pitch_mean", 0.0) or 0.0), 2),
        "pitch_std_hz":    round(float(feats.get("pitch_std", 0.0) or 0.0), 2),
        "pitch_range_hz":  round(float(feats.get("pitch_range", 0.0) or 0.0), 2),
        "jitter":          round(float(feats.get("jitter", 0.0) or 0.0), 6),
        "shimmer":         round(float(feats.get("shimmer", 0.0) or 0.0), 6),
        "hnr":             round(float(feats.get("hnr", 0.0) or 0.0), 4),
        "mfcc_7_std":      round(float(feats.get("mfcc_7_std", 0.0) or 0.0), 4),
        "voiced_ratio":    round(float(feats.get("voiced_ratio", 0.0) or 0.0), 4),
        "zcr_mean":        round(float(feats.get("zcr_mean", 0.0) or 0.0), 6),
    }

    return result


# ─────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
def root():
    return {
        "status": "online",
        "service": "AI Detector Suara (GuardiVoice)",
        "algorithm": "BAMBS (Bio-Acoustic Multi-Boundary Scoring)",
        "model_loaded": detector_instance is not None,
    }


@app.get("/info", tags=["Info"])
def model_info():
    if detector_instance is None:
        return {"status": "model_not_loaded"}

    return {
        "model_name": "BAMBS (Bio-Acoustic Multi-Boundary Scoring)",
        "algorithm": "BAMBS",
        "boundaries_count": len(KEY_BOUNDARIES),
        "boundaries_list": [b["id"] for b in KEY_BOUNDARIES],
        "boundaries_detail": detector_instance.params,
        "metrics": detector_instance.metrics or {
            "test_accuracy": model_meta.get("test_accuracy", 1.0),
            "test_auc": model_meta.get("test_auc", 1.0),
        },
    }


@app.post("/predict", tags=["Prediksi"])
async def predict_audio(file: UploadFile = File(...)):
    """
    Upload file audio (.wav .mp3 .ogg .flac .m4a) dan dapatkan diagnosa 4 batasan akustik.
    """
    allowed_ext = {".wav", ".mp3", ".ogg", ".flac", ".m4a", ".aiff", ".webm"}
    ext = os.path.splitext(file.filename)[-1].lower()
    if ext not in allowed_ext:
        raise HTTPException(
            status_code=400,
            detail=f"Format {ext} tidak didukung. Gunakan salah satu dari: {allowed_ext}"
        )

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        # Ekstraksi fitur audio (maks 30 detik)
        feats = extract_features(tmp_path, duration=30.0)
        if feats is None:
            raise HTTPException(status_code=422, detail="Gagal memproses file audio atau audio kosong.")

        # Eksekusi Algoritma BAMBS
        result = predict_from_features(feats)
        result["filename"] = file.filename

        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error internal server: {str(e)}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


class URLRequest(BaseModel):
    url: str
    filename: str = "audio.wav"

@app.post("/predict-url", tags=["Prediksi"])
async def predict_from_url(req: URLRequest):
    """Prediksi dari tautan/URL audio."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(req.url)
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="URL audio tidak dapat diakses.")

        ext = os.path.splitext(req.filename)[-1].lower() or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(resp.content)
            tmp_path = tmp.name

        feats = extract_features(tmp_path, duration=30.0)
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

        if feats is None:
            raise HTTPException(status_code=422, detail="Gagal memproses file audio.")

        result = predict_from_features(feats)
        result["filename"] = req.filename
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
