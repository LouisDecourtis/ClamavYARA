# HTA Scanner Pipeline (ClamAV + YARA)

Docker image that scans any file—particularly malicious `.hta`—with:

* **ClamAV** signature-based AV, verbose output
* **YARA**  700 + open-source rules (signature-base) + your custom rules

---
## Overview

This project provides a **Docker-based pipeline** to analyse files (e.g. `.hta`) with two engines:

1. **ClamAV** – classic signature antivirus (verbose output)
2. **YARA**  – custom & public threat‐hunting rules (signature-base repository)

## Features

* Scan files with ClamAV and YARA
* Supports custom YARA rules
* Compiles YARA rules at runtime
* Handles external variables dynamically
* Provides detailed output with detections

## Prerequisites

* Docker (20+)

## Quick start

### 1. Build once
```bash
cd yara
docker build -t hta-pipeline .
```
*(Requires Docker ≥ 20)*

### 2. Scan a file
```bash
docker run --rm -v "$(pwd)":/workspace hta-pipeline /workspace/Simulation_rancongiciel.hta
```
Output:
```
=== ClamAV scan ===
Scanning /workspace/Simulation_rancongiciel.hta
/workspace/Simulation_rancongiciel.hta: OK

----------- SCAN SUMMARY -----------
Known viruses: 8707245
Engine version: 0.103.12
Scanned files: 1
Infected files: 0
Time: 12 sec
=== End ClamAV ===
Scanned 715 rules. Detections: 1

┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Rule                     ┃ Tags ┃ Meta                                       ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ custom_detect_ransom_hta │ -    │ author=cascade,description=Detects the     │
│                          │      │ Simulation_rancongiciel.hta test file      │
└──────────────────────────┴──────┴────────────────────────────────────────────┘
```
Exit code `100` if YARA detects anything, `0` otherwise.

---
## Project layout
```
Dockerfile           image definition
run_pipeline.sh      entrypoint (ClamAV → YARA)
scan_with_yara.py    YARA wrapper (handles external vars)
requirements.txt     Python deps (yara-python, rich)
signature-base/      upstream rules + your own *.yar
```

### Add/modify rules
Drop extra `*.yar` / `*.yara` into `signature-base/yara/`. They are compiled at runtime; missing external variables are injected automatically.

### Optional: YARA CLI inside the container
Uncomment in Dockerfile:
```dockerfile
RUN apt-get update && apt-get install -y yara
```
Then you can run:
```bash
docker run --rm -v "$(pwd)":/workspace hta-pipeline \
    yara -r /app/signature-base/yara /workspace/file
```

---
## Performance notes
• Rules compile once per run (~1–2 s).
• Scan speed is I/O bound; a 2 GB file on SSD ~1-4 min.

To benchmark without wasting space:
```bash
fallocate -l 2G big_dummy.bin      # sparse file
/usr/bin/time -v docker run --rm -v "$(pwd)":/workspace \
          hta-pipeline /workspace/big_dummy.bin
rm big_dummy.bin
```

---
## Updating signatures
Run `docker build …` again to refresh ClamAV DB and include latest rule commits.

---
## Exit codes
* `0` – clean
* `100` – YARA detections (see table)
* other – script / engine error

## Notes
* `freshclam` is executed at build time; update the DB periodically by rebuilding.
* The container runs without privileges; only the mounted file is scanned.

[Repo](https://github.com/LouisDecourtis/ClamavYARA)
