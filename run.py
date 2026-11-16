#!/usr/bin/env python3
"""Open index.html in a headless browser and run collection through MP4 export.

    pip install playwright && python -m playwright install chromium
    export XAI_API_KEY=...            # Grok searches X and the web
    export ANTHROPIC_API_KEY=...      # Claude searches the web
    python run.py                     # save today's video (Japan time) in out/
    python run.py --date 2026-11-14 --provider claude
    python run.py --sample            # export the sample script, no API call
    python run.py --formats x         # one format: x, youtube, or pc

This script calls the API itself, so the browser CORS limit does not apply.
"""
import argparse
import asyncio
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def relay(payload: str) -> str:
    req = json.loads(payload)
    url, headers, body = req["url"], dict(req.get("headers") or {}), req.get("body")
    if "api.x.ai" in url and not headers.get("Authorization", "").replace("Bearer", "").strip():
        headers["Authorization"] = "Bearer " + os.environ.get("XAI_API_KEY", "")
    if "api.anthropic.com" in url:
        headers.pop("anthropic-dangerous-direct-browser-access", None)
        if not headers.get("x-api-key"):
            headers["x-api-key"] = os.environ.get("ANTHROPIC_API_KEY", "")
    data = json.dumps(body).encode("utf-8")
    r = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(r, timeout=900) as res:
            text = res.read().decode("utf-8")
            return json.dumps({"status": res.status, "json": json.loads(text)})
    except urllib.error.HTTPError as e:
        return json.dumps({"status": e.code, "text": e.read().decode("utf-8", "replace")})


async def main() -> int:
    from playwright.async_api import async_playwright

    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="YYYY-MM-DD in Japan time. Defaults to today")
    ap.add_argument("--provider", choices=["grok", "claude"], default=None)
    ap.add_argument("--model")
    ap.add_argument("--out", default=str(ROOT / "out"))
    ap.add_argument("--sample", action="store_true", help="Export the sample script without an API call")
    ap.add_argument("--formats", default="x,youtube,pc", help="Formats to export, comma-separated: x, youtube, pc")
    ap.add_argument("--country", default="", help="Country code: JP, US, GB, FR, DE, ES, BR, KR, TW, CN")
    ap.add_argument("--lang", default="", help="Language code: ja, en, fr, de, es, pt, ko, zh-Hans, zh-Hant")
    ap.add_argument("--x-user", default="", help="X username. The video uses posts and replies from accounts this user follows")
    a = ap.parse_args()

    provider = a.provider or ("grok" if os.environ.get("XAI_API_KEY") else "claude")
    if not a.sample and not os.environ.get("XAI_API_KEY" if provider == "grok" else "ANTHROPIC_API_KEY"):
        print("Missing API key. Set XAI_API_KEY or ANTHROPIC_API_KEY.", file=sys.stderr)
        return 2
    q = f"auto=1&provider={provider}&formats={a.formats}"
    if a.sample:
        q += "&sample=1"
    if a.date:
        q += f"&date={a.date}"
    if a.model:
        q += f"&model={a.model}"
    if a.country:
        q += f"&country={a.country}"
    if a.lang:
        q += f"&lang={a.lang}"
    if a.x_user:
        q += "&x=" + a.x_user.lstrip("@")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(channel="chrome")
        except Exception:
            browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 1600}, accept_downloads=True)
        page.on("console", lambda m: print("  [page]", m.text) if "[news-shorts]" in m.text else None)
        page.on("pageerror", lambda e: print("  [error]", e, file=sys.stderr))
        await page.expose_function("nsRelay", lambda s: asyncio.get_running_loop().run_in_executor(None, relay, s))
        downloads = []
        page.on("download", lambda d: downloads.append(d))
        await page.goto((ROOT / "index.html").as_uri() + "?" + q)
        await page.wait_for_function(
            "window.NS && (window.NS.done || window.NS.error || document.getElementById('status').classList.contains('err'))",
            timeout=30 * 60 * 1000, polling=1000)
        err = await page.evaluate(
            "window.NS.error || (document.getElementById('status').classList.contains('err') ? document.getElementById('status').textContent : '')")
        if err:
            print("Failed:", err, file=sys.stderr)
            await browser.close()
            return 1
        want = len([f for f in a.formats.split(",") if f in ("x", "youtube", "pc")])
        for _ in range(120):
            if len(downloads) >= want:
                break
            await asyncio.sleep(0.5)
        if not downloads:
            print("Failed: no video file was produced", file=sys.stderr)
            await browser.close()
            return 1
        st = await page.evaluate("window.NS.state()")
        for d in downloads:
            path = out / d.suggested_filename
            await d.save_as(path)
            print("Saved:", path)
        stem = out / downloads[0].suggested_filename.split("_NewsShorts_")[0]
        base = f"{stem}_NewsShorts_{st['script']['date']}"
        Path(base + ".json").write_text(json.dumps(st["script"], ensure_ascii=False, indent=2), encoding="utf-8")
        Path(base + ".txt").write_text(st["sources"], encoding="utf-8")
        print("Script and sources:", base + ".json / .txt")
        await browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
