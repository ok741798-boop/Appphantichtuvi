#!/usr/bin/env bash
# Tạo môi trường ảo nếu chưa có, cài thư viện rồi chạy server tại http://localhost:5057
set -euo pipefail

cd "$(dirname "$0")/backend"

# Trên Windows, "python3" có thể là lối tắt Microsoft Store không chạy được nên phải thử thật.
PYTHON=""
for candidate in python3 python py; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c "import sys" >/dev/null 2>&1; then
        PYTHON="$candidate"
        break
    fi
done
if [ -z "$PYTHON" ]; then
    echo "Không tìm thấy Python. Hãy cài Python 3.10 trở lên." >&2
    exit 1
fi

if [ ! -d .venv ]; then
    "$PYTHON" -m venv .venv
fi
if [ -x .venv/Scripts/python.exe ]; then
    VENV_PYTHON=.venv/Scripts/python.exe
else
    VENV_PYTHON=.venv/bin/python
fi

"$VENV_PYTHON" -m pip install -q -r requirements.txt
echo "TuVi Analyzer đang chạy tại http://localhost:${PORT:-5057}"
exec "$VENV_PYTHON" app.py
