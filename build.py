#!/usr/bin/env python3
"""Build one self-contained index.html from src/ and assets/.

    python build.py
"""
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


UI_JA = (ROOT / "src" / "ui_ja.js").read_text(encoding="utf-8")
MUSIC = (ROOT / "src" / "music.js").read_text(encoding="utf-8")


def pack(html: str, engine: str, assets: dict, muxer: str = "", sample: str = "") -> str:
    return (
        html.replace("/*__UIJA__*/", UI_JA)
        .replace("/*__MUSIC__*/", MUSIC)
        .replace("/*__MUXER__*/", muxer)
        .replace("/*__ENGINE__*/", engine)
        .replace("/*__ASSETS__*/", json.dumps(assets))
        .replace("/*__SAMPLE__*/", sample)
    )


def stamp(html: str) -> tuple:
    """Put the page's own build id in it; the page compares it with version.json to find a newer copy."""
    h = hashlib.sha1(html.encode("utf-8")).hexdigest()[:12]
    return html.replace("__BUILD_ID__", h), h


def main() -> None:
    muxer = (ROOT / "lib" / "mp4-muxer.js").read_text(encoding="utf-8")
    engine = (ROOT / "src" / "engine.js").read_text(encoding="utf-8")
    sample = json.dumps(
        json.loads((ROOT / "samples" / "2026-11-14.json").read_text(encoding="utf-8")),
        ensure_ascii=False,
    )
    assets = {f"bg_{g}": b64(ROOT / "assets" / f"bg_{g}.jpg") for g in "ABCDE"}
    assets["tracks"] = {n: b64(ROOT / "assets" / f"song_{n}.m4a") for n in ("1", "2", "3")}
    for name, code in (("mp4-muxer.js", muxer), ("engine.js", engine), ("ui_ja.js", UI_JA), ("music.js", MUSIC)):
        if "</script" in code.lower():
            raise SystemExit(f"{name} contains </script")
    license_note = "/* mp4-muxer 5.2.2 (MIT License, Copyright (c) 2023 Vanilagy) — lib/mp4-muxer.LICENSE */\n"
    out, news_id = stamp(pack((ROOT / "src" / "app.html").read_text(encoding="utf-8"), engine, assets, license_note + muxer, sample))
    (ROOT / "index.html").write_text(out, encoding="utf-8")
    print(f"index.html {len(out.encode('utf-8')) / 1048576:.2f} MB")
    ja_assets = {"bg_" + g: assets["bg_" + g] for g in "ABCDE"}
    ja_assets["track"] = assets["tracks"]["1"]
    # ja/ was a page of its own that read NHK's and Asahi's RSS. No Japanese medium is read by RSS any
    # more: the address opens News with Japanese cards, which plays the news githito.xapi collects from X.
    ja = ('<!doctype html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">\n'
          '<meta http-equiv="refresh" content="0; url=../?lang=ja">\n<title>News Shorts</title>\n</head>\n'
          '<body>\n<p><a href="../?lang=ja">News Shorts</a></p>\n'
          '<script>location.replace("../?lang=ja");</script>\n</body>\n</html>\n')
    dest = ROOT / "ja" / "index.html"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(ja, encoding="utf-8")
    print(f"ja/index.html {len(ja.encode('utf-8'))} bytes (opens News in Japanese)")
    humor, humor_id = stamp(pack((ROOT / "src" / "humor.html").read_text(encoding="utf-8"), engine, ja_assets, license_note + muxer))
    humor_dest = ROOT / "humor" / "index.html"
    humor_dest.parent.mkdir(exist_ok=True)
    humor_dest.write_text(humor, encoding="utf-8")
    print(f"humor/index.html {len(humor.encode('utf-8')) / 1048576:.2f} MB")
    (ROOT / "version.json").write_text(json.dumps({"news": news_id, "humor": humor_id}) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
