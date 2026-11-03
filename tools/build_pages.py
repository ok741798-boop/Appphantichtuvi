"""Đóng gói bản tĩnh cho GitHub Pages: frontend, mã Python backend và font cho PDF.

Bản tĩnh chạy backend trong trình duyệt bằng Pyodide (xem frontend/js/pyodide-bridge.js).

    python tools/build_pages.py --out _site --font DejaVuSans.ttf --bold-font DejaVuSans-Bold.ttf
"""

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
MAIN_SCRIPT_TAG = '<script src="js/main.js" defer></script>'
BRIDGE_SCRIPT_TAG = '<script src="js/pyodide-bridge.js"></script>'
# Tên file phải khớp FONT_CANDIDATES trong pdf_report.py.
FONT_NAMES = ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf")


def build(out_dir: Path, font: Path, bold_font: Path) -> None:
    """Tạo thư mục site hoàn chỉnh tại out_dir, xóa bản cũ nếu có."""
    if out_dir.exists():
        shutil.rmtree(out_dir)
    shutil.copytree(FRONTEND_DIR, out_dir)

    # Bridge phải chạy trước main.js để main.js thấy window.tuviPython.
    for page in out_dir.glob("*.html"):
        html = page.read_text(encoding="utf-8")
        if MAIN_SCRIPT_TAG not in html:
            raise SystemExit(f"{page.name} không có thẻ {MAIN_SCRIPT_TAG}")
        page.write_text(html.replace(MAIN_SCRIPT_TAG, f"{BRIDGE_SCRIPT_TAG}\n    {MAIN_SCRIPT_TAG}"),
                        encoding="utf-8")

    py_dir = out_dir / "py"
    py_dir.mkdir()
    modules = sorted(path.name for path in BACKEND_DIR.glob("*.py"))
    for name in modules:
        shutil.copy2(BACKEND_DIR / name, py_dir / name)

    fonts_dir = out_dir / "fonts"
    fonts_dir.mkdir()
    for source, name in zip((font, bold_font), FONT_NAMES):
        shutil.copy2(source, fonts_dir / name)

    manifest = {"modules": modules, "fonts": list(FONT_NAMES)}
    (py_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    # Không để GitHub Pages chạy Jekyll, vì Jekyll bỏ qua file bắt đầu bằng dấu gạch dưới.
    (out_dir / ".nojekyll").touch()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=ROOT / "_site")
    parser.add_argument("--font", type=Path, required=True, help="Font TTF thường hỗ trợ tiếng Việt")
    parser.add_argument("--bold-font", type=Path, required=True, help="Font TTF đậm hỗ trợ tiếng Việt")
    args = parser.parse_args()
    build(args.out, args.font, args.bold_font)
    print(f"Đã tạo bản tĩnh tại {args.out}")


if __name__ == "__main__":
    main()
