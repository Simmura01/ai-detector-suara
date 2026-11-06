"""
train_model.py
==============
Training, kalibrasi, validasi, dan evaluasi algoritma BAMBS
(Bio-Acoustic Multi-Boundary Scoring) menggunakan 4 batasan fisik akustik utama.

Penggunaan:
  python train_model.py
  python train_model.py --csv features.csv --model models
"""

import os
import sys
import io
import csv
import argparse
import warnings
import numpy as np
import joblib

# Pastikan console Windows mendukung output UTF-8 (mencegah charmap error)
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True)

warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, roc_curve, accuracy_score, precision_score, recall_score, f1_score
)
from bambs_algorithm import BAMBSDetector, KEY_BOUNDARIES


# ─────────────────────────────────────────────
# LOAD & PERSIAPKAN DATA
# ─────────────────────────────────────────────

def load_data(csv_path: str):
    """
    Load features.csv tanpa ketergantungan pandas.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File {csv_path} tidak ditemukan!")

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise ValueError(f"File {csv_path} kosong!")

    target_features = [b["id"] for b in KEY_BOUNDARIES]

    X_list = []
    y_list = []
    for r in rows:
        label_str = r.get("label", "").strip().lower()
        if label_str not in ("human", "ai"):
            continue
        y_list.append(1 if label_str == "ai" else 0)

        vals = []
        for feat in target_features:
            try:
                v = r.get(feat, 0.0)
                val = float(v) if v not in ("", None) else 0.0
            except ValueError:
                val = 0.0
            vals.append(val)
        X_list.append(vals)

    X = np.array(X_list, dtype=float)
    y = np.array(y_list, dtype=int)

    print(f"\n📊 Dataset dimuat: {len(X)} sampel dari {csv_path}", flush=True)
    n_human = int(np.sum(y == 0))
    n_ai = int(np.sum(y == 1))
    print(f"   Human : {n_human} sampel", flush=True)
    print(f"   AI    : {n_ai} sampel", flush=True)
    print(f"   4 Batasan Akustik Terpilih: {target_features}\n", flush=True)

    return X, y, target_features


# ─────────────────────────────────────────────
# TRAINING & EVALUASI ALGORITMA BAMBS
# ─────────────────────────────────────────────

def train_and_evaluate(X, y, target_features, output_dir="models"):
    os.makedirs(output_dir, exist_ok=True)

    n_samples = len(X)
    n_ai = int(np.sum(y == 1))
    n_human = int(np.sum(y == 0))
    min_count = min(n_human, n_ai)

    if min_count < 2:
        raise ValueError("Setiap kelas membutuhkan minimal 2 sampel untuk validasi.")

    n_splits = min(5, min_count)
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

    cv_accs, cv_aucs, cv_f1s = [], [], []

    print(f"🔬 Validasi Silang (Stratified {n_splits}-Fold Cross Validation):", flush=True)
    for fold, (train_idx, test_idx) in enumerate(skf.split(X, y), 1):
        X_train, y_train = X[train_idx], y[train_idx]
        X_test, y_test = X[test_idx], y[test_idx]

        detector = BAMBSDetector()
        detector.fit(X_train, y_train, feature_names=target_features)

        test_probs = detector.predict_batch(X_test, feature_names=target_features)
        test_preds = (test_probs >= 0.5).astype(int)

        acc = accuracy_score(y_test, test_preds)
        try:
            auc = roc_auc_score(y_test, test_probs)
        except Exception:
            auc = acc
        f1 = f1_score(y_test, test_preds, zero_division=1)

        cv_accs.append(acc)
        cv_aucs.append(auc)
        cv_f1s.append(f1)
        print(f"   Fold {fold}: Accuracy = {acc:.4f} | ROC-AUC = {auc:.4f} | F1 = {f1:.4f}", flush=True)

    mean_acc = float(np.mean(cv_accs))
    mean_auc = float(np.mean(cv_aucs))
    mean_f1 = float(np.mean(cv_f1s))

    print(f"\n🏆 Hasil Rata-Rata Cross-Validation BAMBS:", flush=True)
    print(f"   Mean Accuracy : {mean_acc:.4f} ± {np.std(cv_accs):.4f}", flush=True)
    print(f"   Mean ROC-AUC  : {mean_auc:.4f} ± {np.std(cv_aucs):.4f}", flush=True)
    print(f"   Mean F1-Score : {mean_f1:.4f} ± {np.std(cv_f1s):.4f}\n", flush=True)

    # ── Fit model final pada seluruh dataset ──────────────────────────────
    final_detector = BAMBSDetector()
    final_detector.fit(X, y, feature_names=target_features)

    full_probs = final_detector.predict_batch(X, feature_names=target_features)
    full_preds = (full_probs >= 0.5).astype(int)

    final_acc = float(accuracy_score(y, full_preds))
    try:
        final_auc = float(roc_auc_score(y, full_probs))
    except Exception:
        final_auc = final_acc

    final_prec = float(precision_score(y, full_preds, zero_division=1))
    final_rec = float(recall_score(y, full_preds, zero_division=1))
    final_f1 = float(f1_score(y, full_preds, zero_division=1))

    print("📈 Evaluasi Model Final (Full Dataset):", flush=True)
    print(f"   Accuracy  : {final_acc:.4f}", flush=True)
    print(f"   ROC-AUC   : {final_auc:.4f}", flush=True)
    print(f"   Precision : {final_prec:.4f}", flush=True)
    print(f"   Recall    : {final_rec:.4f}", flush=True)
    print(f"   F1-Score  : {final_f1:.4f}\n", flush=True)
    print(classification_report(y, full_preds, target_names=["Human", "AI"]), flush=True)

    print("📋 Rincian Ambang Batas (Decision Boundaries) Terkalibrasi:")
    for b in KEY_BOUNDARIES:
        p = final_detector.params[b["id"]]
        print(f"   • {p['name']} ({p['id']}):")
        print(f"       Threshold (θ) : {p['theta']} {p['unit']}")
        print(f"       Bobot (w)     : {p['weight']*100:.1f}% (Cohen's d = {p['cohen_d']})")
        print(f"       Zona Human    : Mean {p['h_mean']} ± {p['h_std']}")
        print(f"       Zona AI       : Mean {p['a_mean']} ± {p['a_std']}")

    final_detector.metrics = {
        "cv_accuracy": round(mean_acc, 4),
        "cv_auc": round(mean_auc, 4),
        "cv_f1": round(mean_f1, 4),
        "test_accuracy": round(final_acc, 4),
        "test_auc": round(final_auc, 4),
        "precision": round(final_prec, 4),
        "recall": round(final_rec, 4),
        "f1": round(final_f1, 4),
        "sample_count": len(X),
        "features": target_features,
    }

    # ── 1. Visualisasi Confusion Matrix ───────────────────────────────────
    cm = confusion_matrix(y, full_preds)
    plt.figure(figsize=(5.5, 4.2))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Human", "AI"],
                yticklabels=["Human", "AI"],
                cbar=False, annot_kws={"size": 14, "weight": "bold"})
    plt.title("Confusion Matrix — BAMBS Algorithm", fontsize=12, fontweight="bold", pad=12)
    plt.ylabel("Aktual (Ground Truth)", fontsize=10)
    plt.xlabel("Prediksi Algoritma", fontsize=10)
    plt.tight_layout()
    cm_path = os.path.join(output_dir, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=180)
    plt.close()
    print(f"\n   ✓ Confusion matrix disimpan: {cm_path}", flush=True)

    # ── 2. Visualisasi ROC Curve ──────────────────────────────────────────
    try:
        fpr, tpr, _ = roc_curve(y, full_probs)
        plt.figure(figsize=(5.5, 4.2))
        plt.plot(fpr, tpr, label=f"BAMBS (AUC = {final_auc:.4f})", color="#6366f1", lw=2.5)
        plt.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5, label="Random Guess")
        plt.xlabel("False Positive Rate", fontsize=10)
        plt.ylabel("True Positive Rate", fontsize=10)
        plt.title("ROC Curve — 4 Batasan Akustik", fontsize=12, fontweight="bold", pad=12)
        plt.legend(loc="lower right", frameon=True)
        plt.grid(alpha=0.2)
        plt.tight_layout()
        roc_path = os.path.join(output_dir, "roc_curve.png")
        plt.savefig(roc_path, dpi=180)
        plt.close()
        print(f"   ✓ ROC curve disimpan: {roc_path}", flush=True)
    except Exception as e:
        print(f"   [!] Gagal membuat ROC curve: {e}", flush=True)

    # ── 3. Visualisasi 4 Batasan & Distribusi Data ─────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    axes = axes.flatten()

    for idx, b in enumerate(KEY_BOUNDARIES):
        ax = axes[idx]
        fid = b["id"]
        p = final_detector.params[fid]

        h_vals = X[y == 0, idx]
        a_vals = X[y == 1, idx]

        # Scatter jitter
        np.random.seed(42)
        y_h = np.random.normal(0, 0.04, size=len(h_vals))
        y_a = np.random.normal(1, 0.04, size=len(a_vals))

        ax.scatter(h_vals, y_h, color="#10b981", alpha=0.75, s=45, label="Human")
        ax.scatter(a_vals, y_a, color="#ef4444", alpha=0.75, s=45, label="AI")

        # Threshold vertical line
        ax.axvline(p["theta"], color="#6366f1", linestyle="--", linewidth=2,
                   label=f"Batas θ = {p['theta']}")

        ax.set_yticks([0, 1])
        ax.set_yticklabels(["Human", "AI"])
        ax.set_title(f"{p['name']}\n(Bobot: {p['weight']*100:.1f}%, Cohen's d: {p['cohen_d']})",
                     fontsize=10, fontweight="bold")
        ax.set_xlabel(f"Nilai ({p['unit']})", fontsize=9)
        ax.grid(alpha=0.2)
        ax.legend(fontsize=8, loc="upper right")

    plt.suptitle("Pemisahan Data Berdasarkan 4 Batasan Akustik (BAMBS)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    boundaries_path = os.path.join(output_dir, "feature_importance.png")
    boundaries_detail_path = os.path.join(output_dir, "boundaries_visualization.png")
    plt.savefig(boundaries_path, dpi=180)
    plt.savefig(boundaries_detail_path, dpi=180)
    plt.close()
    print(f"   ✓ Visualisasi 4 batasan disimpan: {boundaries_detail_path}", flush=True)

    # ── 4. Simpan Model & Metadata ────────────────────────────────────────
    rules_json_path = os.path.join(output_dir, "detector_rules.json")
    final_detector.save_json(rules_json_path)
    print(f"   ✓ Konfigurasi aturan disimpan ke: {rules_json_path}", flush=True)

    # Simpan detector.pkl kompatibel dengan main.py
    model_path = os.path.join(output_dir, "detector.pkl")
    meta = {
        "model": final_detector,
        "detector": final_detector,
        "model_name": "BAMBS (Bio-Acoustic Multi-Boundary Scoring)",
        "algorithm": "BAMBS",
        "feature_names": target_features,
        "test_accuracy": round(final_acc, 4),
        "test_auc": round(final_auc, 4),
        "precision": round(final_prec, 4),
        "recall": round(final_rec, 4),
        "f1": round(final_f1, 4),
        "params": final_detector.params,
    }
    joblib.dump(meta, model_path)
    print(f"\n💾 Model BAMBS berhasil disimpan ke: {model_path}\n", flush=True)
    return meta


# ─────────────────────────────────────────────
# MAIN CLI
# ─────────────────────────────────────────────

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description="Training Algoritma BAMBS (4 Batasan Akustik)")
    parser.add_argument("--csv",   type=str, default=os.path.join(base_dir, "features.csv"), help="Path ke features.csv")
    parser.add_argument("--model", type=str, default=os.path.join(base_dir, "models"),       help="Folder penyimpanan model")
    args = parser.parse_args()

    X, y, target_features = load_data(args.csv)
    train_and_evaluate(X, y, target_features, output_dir=args.model)
