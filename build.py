#!/usr/bin/env python3
"""Build one self-contained index.html from src/ and assets/.

    python build.py
"""
import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def pack(html: str, engine: str, assets: dict, muxer: str = "", sample: str = "") -> str:
    return (
        html.replace("/*__MUXER__*/", muxer)
        .replace("/*__ENGINE__*/", engine)
        .replace("/*__ASSETS__*/", json.dumps(assets))
        .replace("/*__SAMPLE__*/", sample)
    )


def main() -> None:
    muxer = (ROOT / "lib" / "mp4-muxer.js").read_text(encoding="utf-8")
    engine = (ROOT / "src" / "engine.js").read_text(encoding="utf-8")
    sample = json.dumps(
        json.loads((ROOT / "samples" / "2026-11-14.json").read_text(encoding="utf-8")),
        ensure_ascii=False,
    )
    assets = {f"bg_{g}": b64(ROOT / "assets" / f"bg_{g}.jpg") for g in "ABCDE"}
    assets["tracks"] = {
        "jupiter": b64(ROOT / "assets" / "jupiter_1922.m4a"),
        "neptune": b64(ROOT / "assets" / "neptune_1923.m4a"),
        "stripes": b64(ROOT / "assets" / "stripes_1909.m4a"),
        "sandman": b64(ROOT / "assets" / "sandman_1920.m4a"),
    }
    for name, code in (("mp4-muxer.js", muxer), ("engine.js", engine)):
        if "</script" in code.lower():
            raise SystemExit(f"{name} contains </script")
    license_note = "/* mp4-muxer 5.2.2 (MIT License, Copyright (c) 2023 Vanilagy) — lib/mp4-muxer.LICENSE */\n"
    out = pack((ROOT / "src" / "app.html").read_text(encoding="utf-8"), engine, assets, license_note + muxer, sample)
    (ROOT / "index.html").write_text(out, encoding="utf-8")
    print(f"index.html {len(out.encode('utf-8')) / 1048576:.2f} MB")
    ja_assets = {"bg_" + g: assets["bg_" + g] for g in "ABCDE"}
    ja_assets["track"] = assets["tracks"]["jupiter"]
    ja = pack((ROOT / "src" / "ja.html").read_text(encoding="utf-8"), engine, ja_assets)
    dest = ROOT / "ja" / "index.html"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(ja, encoding="utf-8")
    print(f"ja/index.html {len(ja.encode('utf-8')) / 1048576:.2f} MB")
    # Humor stays in src/humor.html and is unpublished for now.
    humor_dest = ROOT / "humor" / "index.html"
    if humor_dest.exists():
        humor_dest.unlink()
        print("humor/index.html removed")


if __name__ == "__main__":
    main()
