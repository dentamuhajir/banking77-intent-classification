"""Latih satu baseline pada indeks fitting resmi proyek dan ukur macro-F1 validasi."""

import argparse
import csv
import hashlib
import json
import platform
import warnings
from pathlib import Path
from tempfile import TemporaryDirectory

import joblib
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import f1_score
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC


ROOT = Path(__file__).resolve().parents[1]
DEMO = "When will my card arrive?"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def train(data_dir, output_dir, run_name):
    manifest = load_json(data_dir / "raw/manifest.json")
    train_path = data_dir / "raw/train.csv"
    if sha256(train_path) != manifest["files"]["train.csv"]["sha256"]:
        raise ValueError("Checksum train.csv berbeda dari manifes audit")
    with train_path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    split_path = data_dir / "processed/split_indices.json"
    split = load_json(split_path)
    labels = load_json(data_dir / "processed/label_mapping.json")["id_to_label"]
    fit_ids, val_ids = split["fitting_row_ids"], split["validation_row_ids"]
    if sorted(fit_ids + val_ids) != list(range(len(rows))):
        raise ValueError("Indeks fitting dan validasi harus mencakup setiap baris tepat sekali")
    fit_y = [rows[i]["category"] for i in fit_ids]
    val_y = [rows[i]["category"] for i in val_ids]
    if set(fit_y) != set(labels) or set(val_y) != set(labels):
        raise ValueError("Kelas fitting atau validasi berbeda dari pemetaan label")

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 1), min_df=1)),
        ("svm", LinearSVC(C=1.0, random_state=42, max_iter=1000)),
    ])
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always", ConvergenceWarning)
        pipeline.fit([rows[i]["text"] for i in fit_ids], fit_y)
    val_text = [rows[i]["text"] for i in val_ids]
    predictions = pipeline.predict(val_text)
    score = f1_score(val_y, predictions, labels=labels, average="macro")
    demo_label = pipeline.predict([DEMO])[0]

    model_path = output_dir / "models" / f"svm_baseline_{run_name}.joblib"
    result_path = output_dir / "results" / f"svm_baseline_{run_name}.json"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=model_path.parent) as tmp:
        staged = Path(tmp) / model_path.name
        joblib.dump(pipeline, staged, compress=3)
        restored = joblib.load(staged)
        if (restored.predict(val_text) != predictions).any() or restored.predict([DEMO])[0] != demo_label:
            raise ValueError("Prediksi berubah sesudah pipeline dimuat ulang")
        report = {
            "run": run_name, "python": platform.python_version(), "platform": platform.platform(),
            "scikit_learn": sklearn.__version__, "data_revision": manifest["revision"],
            "split_sha256": sha256(split_path), "split_seed": split["seed"],
            "fitting_rows": len(fit_ids), "validation_rows": len(val_ids), "classes": len(labels),
            "ngram_range": [1, 1], "min_df": 1, "C": 1.0, "svm_seed": 42,
            "max_iter": 1000, "iterations": int(pipeline["svm"].n_iter_),
            "converged": not any(issubclass(w.category, ConvergenceWarning) for w in captured),
            "validation_macro_f1": float(score), "reload_matches": len(predictions),
            "demo_text": DEMO, "demo_label": str(demo_label),
            "model_filename": model_path.name, "model_sha256": sha256(staged),
        }
        staged.replace(model_path)
    with TemporaryDirectory(dir=result_path.parent) as tmp:
        staged = Path(tmp) / result_path.name
        staged.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        staged.replace(result_path)
    print(f"Macro-F1 validasi = {score:.6f}\n{DEMO} -> {demo_label}\n{result_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run-name", choices=("local", "colab"), required=True)
    args = parser.parse_args()
    train(args.data_dir, args.output_dir, args.run_name)
