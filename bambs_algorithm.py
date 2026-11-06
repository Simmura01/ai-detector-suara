"""
bambs_algorithm.py
==================
Bio-Acoustic Multi-Boundary Scoring (BAMBS) Algorithm.
Algoritma Kustom Berbasis 4 Batasan Fisik Akustik untuk Deteksi Suara Manusia vs AI.

Dikembangkan untuk proyek AI Detector Suara (GuardiVoice).
Keunggulan:
  1. Explainable AI (XAI) - 100% transparan, bukan black-box.
  2. Bebas Overfitting - Berdasarkan 4 parameter fisik bio-akustik fundamental.
  3. Diagnosa Per Batasan - Memberikan alasan terperinci pelanggaran tiap batasan.
"""

import json
import os
import numpy as np


# Definisi 4 Batasan Kunci
KEY_BOUNDARIES = [
    {
        "id": "pitch_range",
        "name": "Rentang Dinamika Nada (Pitch Range)",
        "unit": "Hz",
        "direction": -1,  # Nilai lebih rendah -> AI (monoton)
        "desc_human": "Variasi nada dinamis & ekspresif khas biologis manusia",
        "desc_ai": "Intonasi nada terbatas/monoton khas sintesis TTS",
    },
    {
        "id": "shimmer",
        "name": "Perturbasi Mikro-Amplitudo (Shimmer)",
        "unit": "rasio",
        "direction": 1,  # Nilai lebih tinggi -> AI (artifak modulasi vocoder)
        "desc_human": "Mikro-fluktuasi amplitudo getaran glotis organik normal",
        "desc_ai": "Artifak fluktuasi amplitudo mikroskopis dari neural vocoder",
    },
    {
        "id": "hnr",
        "name": "Harmonic-to-Noise Ratio (HNR)",
        "unit": "rasio",
        "direction": -1,  # Nilai lebih rendah -> AI (kehilangan desah napas alami)
        "desc_human": "Resonansi harmonik kaya dengan desah udara pita suara alami",
        "desc_ai": "Distorsi harmonik sintetis tanpa dinamika respirasi biologis",
    },
    {
        "id": "mfcc_7_std",
        "name": "Dispersi Formant Spektral (MFCC-7)",
        "unit": "koefisien",
        "direction": 1,  # Nilai lebih tinggi -> AI (dispersi khas upsampling vocoder)
        "desc_human": "Koherensi formasi vokal rongga laring dan mulut manusia",
        "desc_ai": "Jejak dispersi spektral akibat upsampling konvolusi neural network",
    },
]


class BAMBSDetector:
    """
    Bio-Acoustic Multi-Boundary Scoring Detector.
    """

    def __init__(self, config=None):
        self.feature_names = [b["id"] for b in KEY_BOUNDARIES]
        self.boundaries_meta = {b["id"]: b for b in KEY_BOUNDARIES}
        self.params = {}
        self.metrics = {}
        if config:
            self.load_from_dict(config)

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names=None):
        """
        Kalibrasi ambang batas (threshold theta), slope (tau), dan bobot (weight)
        berdasarkan distribusi empiris Human (y=0) dan AI (y=1).

        Parameters
        ----------
        X : np.ndarray, shape (n_samples, 4)
        y : np.ndarray, shape (n_samples,) dengan nilai 0 (human) atau 1 (ai)
        """
        if feature_names is None:
            feature_names = self.feature_names

        name_to_idx = {name: i for i, name in enumerate(feature_names)}
        self.params = {}
        weights = []

        for b in KEY_BOUNDARIES:
            fid = b["id"]
            idx = name_to_idx[fid]
            x_i = X[:, idx]

            h_vals = x_i[y == 0]
            a_vals = x_i[y == 1]

            h_mean = float(np.mean(h_vals))
            h_std = float(np.std(h_vals, ddof=1)) if len(h_vals) > 1 else 1.0
            a_mean = float(np.mean(a_vals))
            a_std = float(np.std(a_vals, ddof=1)) if len(a_vals) > 1 else 1.0

            # Pooled standard deviation
            pooled_std = float(np.sqrt(0.5 * (h_std ** 2 + a_std ** 2)))
            if pooled_std < 1e-6:
                pooled_std = 1e-4

            # Optimal Bayes decision threshold (weighted intersection)
            theta = (h_mean * a_std + a_mean * h_std) / (h_std + a_std + 1e-9)

            # Slope scale
            tau = max(pooled_std * 0.75, 1e-4)

            # Cohen's d effect size (kekuatan pemisahan)
            cohen_d = float(abs(h_mean - a_mean) / pooled_std)
            weights.append(cohen_d)

            self.params[fid] = {
                "id": fid,
                "name": b["name"],
                "unit": b["unit"],
                "direction": b["direction"],
                "theta": round(float(theta), 4),
                "tau": round(float(tau), 4),
                "h_mean": round(h_mean, 4),
                "h_std": round(h_std, 4),
                "a_mean": round(a_mean, 4),
                "a_std": round(a_std, 4),
                "cohen_d": round(cohen_d, 3),
                "desc_human": b["desc_human"],
                "desc_ai": b["desc_ai"],
            }

        # Normalisasi bobot sehingga total sum = 1.0
        weights = np.array(weights)
        weights_norm = weights / np.sum(weights)
        for i, b in enumerate(KEY_BOUNDARIES):
            fid = b["id"]
            self.params[fid]["weight"] = round(float(weights_norm[i]), 4)

        return self

    def predict_score_single(self, feat_val: float, fid: str) -> dict:
        """
        Hitung skor pelanggaran satu batasan (0 = 100% human-like, 1 = 100% ai-like).
        """
        p = self.params.get(fid)
        if not p:
            return {"score": 0.5, "zone": "unknown", "status": "Tidak Diketahui"}

        direction = p["direction"]
        theta = p["theta"]
        tau = p["tau"]

        # Z-score terarah terhadap threshold
        z = direction * (feat_val - theta) / tau
        score = 1.0 / (1.0 + np.exp(-np.clip(z, -15.0, 15.0)))

        # Penentuan status lolos batasan
        is_ai_zone = (direction == 1 and feat_val > theta) or (direction == -1 and feat_val < theta)
        zone = "ai" if is_ai_zone else "human"
        status = "Artifisial (Melanggar)" if is_ai_zone else "Alami (Lolos)"
        explanation = p["desc_ai"] if is_ai_zone else p["desc_human"]

        return {
            "id": fid,
            "name": p["name"],
            "unit": p["unit"],
            "value": round(float(feat_val), 4),
            "threshold": p["theta"],
            "score": round(float(score), 4),
            "zone": zone,
            "status": status,
            "weight": p["weight"],
            "explanation": explanation,
            "direction": direction,
        }

    def predict(self, feats_dict: dict) -> dict:
        """
        Melakukan evaluasi lengkap pada 4 batasan dan mengembalikan diagnosa lengkap.
        """
        boundaries_result = {}
        composite_ai_prob = 0.0

        for b in KEY_BOUNDARIES:
            fid = b["id"]
            val = float(feats_dict.get(fid, 0.0) or 0.0)
            single_res = self.predict_score_single(val, fid)
            boundaries_result[fid] = single_res
            weight = self.params[fid].get("weight", 0.25)
            composite_ai_prob += weight * single_res["score"]

        composite_ai_prob = float(np.clip(composite_ai_prob, 0.0001, 0.9999))
        composite_human_prob = 1.0 - composite_ai_prob

        is_ai = composite_ai_prob >= 0.5
        label = "ai" if is_ai else "human"
        verdict = "Suara AI (Sintetis)" if is_ai else "Suara Manusia Asli"
        confidence = round(max(composite_ai_prob, composite_human_prob) * 100.0, 2)

        # Hitung ringkasan pelanggaran
        violations_count = sum(1 for res in boundaries_result.values() if res["zone"] == "ai")

        return {
            "algorithm": "BAMBS (Bio-Acoustic Multi-Boundary Scoring)",
            "label": label,
            "label_id": 1 if is_ai else 0,
            "confidence": confidence,
            "probabilities": {
                "human": round(composite_human_prob, 4),
                "ai": round(composite_ai_prob, 4),
            },
            "verdict": verdict,
            "violations_count": violations_count,
            "total_boundaries": len(KEY_BOUNDARIES),
            "boundaries": boundaries_result,
            "summary_text": (
                f"Audio terdeteksi sebagai {verdict} dengan keyakinan {confidence}%. "
                f"{violations_count} dari {len(KEY_BOUNDARIES)} batasan menunjukkan pola artifisial."
            ),
        }

    def predict_batch(self, X: np.ndarray, feature_names=None) -> np.ndarray:
        """
        Prediksi batch probabilitas AI untuk matriks X.
        """
        if feature_names is None:
            feature_names = self.feature_names
        name_to_idx = {name: i for i, name in enumerate(feature_names)}

        probs = []
        for x in X:
            fdict = {fid: x[name_to_idx[fid]] for fid in self.feature_names}
            res = self.predict(fdict)
            probs.append(res["probabilities"]["ai"])
        return np.array(probs)

    def to_dict(self) -> dict:
        return {
            "algorithm": "BAMBS",
            "version": "2.0.0",
            "feature_names": self.feature_names,
            "params": self.params,
            "metrics": self.metrics,
        }

    def load_from_dict(self, d: dict):
        self.feature_names = d.get("feature_names", self.feature_names)
        self.params = d.get("params", {})
        self.metrics = d.get("metrics", {})

    def save_json(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_json(cls, path: str):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        return cls(config=d)
