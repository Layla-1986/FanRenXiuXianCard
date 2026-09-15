# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

root = Path(SPECPATH)
datas = [
    (str(root / "quota-card-app.html"), "."),
    (str(root / "scripts" / "quota-card-app.js"), "scripts"),
    (str(root / "scripts" / "collect_antigravity_quota.ps1"), "scripts"),
    (str(root / "styles" / "mortal-seal-card.css"), "styles"),
    (str(root / "assets" / "hanli-nangong-background.png"), "assets"),
    (str(root / "assets" / "antigravity-nangong-background.jpg"), "assets"),
    (str(root / "assets" / "mortal-quota-card.ico"), "assets"),
]

a = Analysis(
    [str(root / "quota_card_app.py")], pathex=[str(root)], binaries=[], datas=datas,
    hiddenimports=["webview.platforms.edgechromium", "pystray._win32"],
    hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True, name="MortalQuotaCard", debug=False,
    bootloader_ignore_signals=False, strip=False, upx=True, console=False,
    icon=str(root / "assets" / "mortal-quota-card.ico"),
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=True, name="MortalQuotaCard")
