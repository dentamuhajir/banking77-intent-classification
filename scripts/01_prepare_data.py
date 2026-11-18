"""Verifikasi sumber Banking77, audit, lalu buat split bersama untuk SVM dan BERT."""

import argparse
import csv
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import urlopen

from sklearn.model_selection import train_test_split


ROOT = Path(__file__).resolve().parents[1]
SEED = 42
FIELDS = ("row_id", "text", "normalized_text", "category", "label_id")


def verify_source(raw, manifest):
    raw.mkdir(parents=True, exist_ok=True)
    for name, spec in manifest["files"].items():
        path = raw / name
        if path.exists():
            contents = path.read_bytes()
        else:
            with urlopen(spec["url"], timeout=60) as response:
                contents = response.read()
        if hashlib.sha256(contents).hexdigest() != spec["sha256"]:
            raise ValueError(f"Checksum berbeda untuk {path}")
        if not path.exists():
            with TemporaryDirectory(dir=raw) as tmp:
                verified = Path(tmp) / name
                verified.write_bytes(contents)
                verified.replace(path)


def describe(values):
    return {"min": min(values), "median": statistics.median(values),
            "mean": statistics.mean(values), "max": max(values)}


def inspect_csv(path, label_ids):
    groups = defaultdict(list)
    rows = []
    counts = Counter()
    empty_text = []
    empty_label = []
    unknown_label = []
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["text", "category"]:
            raise ValueError(f"Kolom tidak sesuai di {path}: {reader.fieldnames}")
        for i, record in enumerate(reader):
            text, label = record["text"], record["category"]
            key = " ".join(text.split())
            row = dict(row_id=i, text=text, normalized_text=key, category=label,
                       label_id=label_ids.get(label))
            rows.append(row)
            groups[key].append(row)
            counts[label] += 1
            if not key:
                empty_text.append(i)
            if not label:
                empty_label.append(i)
            elif label not in label_ids:
                unknown_label.append(i)

    sizes = [len(group) for group in groups.values() if len(group) > 1]
    conflicts = [[r["row_id"] for r in group] for group in groups.values()
                 if len({r["category"] for r in group}) > 1]
    report = {
        "columns": reader.fieldnames, "rows": len(rows), "labels_observed": len(counts),
        "counts_by_label": dict(sorted(counts.items())),
        "class_size": describe([counts[label] for label in label_ids]),
        "characters": describe([len(r["text"]) for r in rows]),
        "words": describe([len(r["text"].split()) for r in rows]),
        "empty_text_ids": empty_text, "empty_label_ids": empty_label,
        "unknown_label_ids": unknown_label, "conflicting_groups_row_ids": conflicts,
        "duplicate_groups": len(sizes), "extra_duplicate_rows": sum(n - 1 for n in sizes),
    }
    return rows, groups, report


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8", newline="\n")


def prepare(data_dir):
    raw, processed = data_dir / "raw", data_dir / "processed"
    manifest = json.loads((ROOT / "data/raw/manifest.json").read_text(encoding="utf-8"))
    verify_source(raw, manifest)
    labels = json.loads((raw / "categories.json").read_text(encoding="utf-8"))
    label_ids = {label: i for i, label in enumerate(labels)}
    if len(labels) != 77 or len(label_ids) != 77:
        raise ValueError("Daftar resmi harus mengandung 77 label unik")
    train, train_groups, train_report = inspect_csv(raw / "train.csv", label_ids)
    test, test_groups, test_report = inspect_csv(raw / "test.csv", label_ids)
    shared = sorted(train_groups.keys() & test_groups.keys())
    overlap = [{"train_ids": [r["row_id"] for r in train_groups[key]],
                "test_ids": [r["row_id"] for r in test_groups[key]],
                "label_conflict": len({r["category"] for r in train_groups[key] + test_groups[key]}) > 1}
               for key in shared]
    report = {"revision": manifest["revision"], "train": train_report,
              "test": test_report, "train_test_overlap_groups": overlap}
    processed.mkdir(parents=True, exist_ok=True)
    if len(train) != 10003 or len(test) != 3080 or any(
        audit["empty_text_ids"] or audit["empty_label_ids"] or audit["unknown_label_ids"]
        or audit["conflicting_groups_row_ids"] for audit in (train_report, test_report)
    ):
        write_json(processed / "audit_report.json", report)
        raise ValueError("Periksa anomali pada audit_report.json sebelum membagi data")

    keys = list(train_groups)
    _, valid_keys = train_test_split(keys, test_size=0.2, random_state=SEED,
                                     stratify=[train_groups[k][0]["category"] for k in keys])
    valid_keys = set(valid_keys)
    fitting = [r for r in train if r["normalized_text"] not in valid_keys]
    validation = [r for r in train if r["normalized_text"] in valid_keys]
    fit_ids = [r["row_id"] for r in fitting]
    val_ids = [r["row_id"] for r in validation]
    ids_disjoint = set(fit_ids).isdisjoint(val_ids)
    groups_disjoint = {r["normalized_text"] for r in fitting}.isdisjoint(valid_keys)
    covered = all({r["category"] for r in subset} == set(labels) for subset in (fitting, validation))
    if not (ids_disjoint and groups_disjoint and covered and len(fitting) + len(validation) == len(train)):
        raise ValueError("Pemeriksaan integritas split gagal")
    split = {"dataset": "PolyAI/banking77", "seed": SEED, "total_train_rows": len(train),
             "fitting_count": len(fitting), "validation_count": len(validation),
             "num_classes_in_fitting": len(labels), "num_classes_in_validation": len(labels),
             "zero_leakage_verified": ids_disjoint, "zero_group_overlap_verified": groups_disjoint,
             "fitting_row_ids": fit_ids, "validation_row_ids": val_ids}
    with TemporaryDirectory(dir=processed) as tmp:
        staging = Path(tmp)
        write_json(staging / "audit_report.json", report)
        write_json(staging / "label_mapping.json", {"id_to_label": labels, "label_to_id": label_ids})
        write_json(staging / "split_indices.json", split)
        for name, rows in (("fitting", fitting), ("validation", validation), ("test", test)):
            with (staging / f"{name}.csv").open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(rows)
        for file in staging.iterdir():
            file.replace(processed / file.name)
    print(f"Fitting {len(fitting)}, validasi {len(validation)}, irisan train-test {len(shared)} kelompok.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    prepare(parser.parse_args().data_dir)
