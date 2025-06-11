#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <file_to_scan>" >&2
  exit 1
fi

FILE=$1

echo "=== ClamAV scan ==="
clamscan -v --stdout "$FILE" || true
echo "=== End ClamAV ==="

echo "=== YARA scan ==="
python3 /app/scan_with_yara.py "$FILE"
