"""Rekam lingkungan eksekusi dari interpreter yang dipakai."""

import argparse
import json
import os
import platform
from importlib import metadata
from pathlib import Path

import psutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    output = parser.parse_args().output
    versions = {}
    for package in ("numpy", "scipy", "scikit-learn", "joblib", "threadpoolctl",
                    "psutil", "torch", "transformers"):
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            versions[package] = None
    info = {
        "os": platform.platform(),
        "python": platform.python_version(),
        "cpu": platform.processor() or platform.machine(),
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_threads": os.cpu_count(),
        "ram_bytes": psutil.virtual_memory().total,
        "packages": versions,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
