"""Muat satu pipeline SVM dari disk dan cetak label intent untuk satu pertanyaan."""

import argparse
from pathlib import Path

import joblib


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("text")
    args = parser.parse_args()
    if not args.text.strip():
        parser.error("Pertanyaan harus berisi teks")
    print(joblib.load(args.model).predict([args.text.strip()])[0])
