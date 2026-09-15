from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "images"
EDGE_CANDIDATES = (
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
)


def edge_path() -> Path:
    for candidate in EDGE_CANDIDATES:
        if candidate.exists():
            return candidate
    discovered = shutil.which("msedge")
    if discovered:
        return Path(discovered)
    raise FileNotFoundError("Microsoft Edge was not found")


def page_html(source: str, page: str) -> str:
    html = source.replace('<script src="/scripts/quota-card-app.js"></script>', "")
    if page == "codex":
        return html
    html = re.sub(r'(<iframe id="page-codex"[^>]*)(>)', r'\1 hidden\2', html, count=1)
    html = re.sub(r'(<iframe id="page-antigravity"[^>]*) hidden(>)', r'\1\2', html, count=1)
    return html


def capture(edge: Path, html_path: Path, output_path: Path, profile: Path) -> None:
    subprocess.run(
        [
            str(edge),
            "--headless=new",
            "--disable-gpu",
            "--allow-file-access-from-files",
            f"--user-data-dir={profile}",
            "--force-device-scale-factor=4",
            "--window-size=480,270",
            "--hide-scrollbars",
            "--virtual-time-budget=3000",
            "--run-all-compositor-stages-before-draw",
            f"--screenshot={output_path}",
            html_path.as_uri(),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=30,
    )


def main() -> None:
    source = (ROOT / "quota-card-app.html").read_text(encoding="utf-8")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    edge = edge_path()
    with tempfile.TemporaryDirectory(prefix="mortal-quota-card-") as temp:
        temp_dir = Path(temp)
        for page in ("codex", "antigravity"):
            html_path = ROOT / f".capture-{page}.html"
            try:
                html_path.write_text(page_html(source, page), encoding="utf-8")
                capture(
                    edge,
                    html_path,
                    OUTPUT / f"mortal-quota-card-{page}-hd.png",
                    temp_dir / page,
                )
            finally:
                html_path.unlink(missing_ok=True)
    print("Created 1920x1080 documentation screenshots")


if __name__ == "__main__":
    main()
