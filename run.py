#!/usr/bin/env python3
"""index.html を画面なしのブラウザで開き、ニュース集め → 台本 → MP4 まで自動で行う。

    pip install playwright && python -m playwright install chromium
    export XAI_API_KEY=...            # Grok を使うとき（X とウェブを検索）
    export ANTHROPIC_API_KEY=...      # Claude を使うとき（ウェブを検索）
    python run.py                     # 今日（日本時間）の動画を out/ に保存
    python run.py --date 2026-11-14 --provider claude
    python run.py --sample            # 見本の台本で書き出すだけ（APIを使わない）

APIへの通信はこのスクリプトが代わりに行うので、ブラウザの制限（CORS）を受けない。
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
    ap.add_argument("--date", help="YYYY-MM-DD（日本時間）。省略すると今日")
    ap.add_argument("--provider", choices=["grok", "claude"], default=None)
    ap.add_argument("--model")
    ap.add_argument("--out", default=str(ROOT / "out"))
    ap.add_argument("--sample", action="store_true", help="見本の台本で書き出す")
    a = ap.parse_args()

    provider = a.provider or ("grok" if os.environ.get("XAI_API_KEY") else "claude")
    if not a.sample and not os.environ.get("XAI_API_KEY" if provider == "grok" else "ANTHROPIC_API_KEY"):
        print("APIキーがありません（XAI_API_KEY か ANTHROPIC_API_KEY）", file=sys.stderr)
        return 2
    q = f"auto=1&provider={provider}"
    if a.sample:
        q += "&sample=1"
    if a.date:
        q += f"&date={a.date}"
    if a.model:
        q += f"&model={a.model}"
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
            print("失敗:", err, file=sys.stderr)
            await browser.close()
            return 1
        for _ in range(120):
            if downloads:
                break
            await asyncio.sleep(0.5)
        if not downloads:
            print("失敗: 動画のファイルが出てきませんでした", file=sys.stderr)
            await browser.close()
            return 1
        d = downloads[0]
        st = await page.evaluate("window.NS.state()")
        path = out / (st.get("name") or d.suggested_filename)
        await d.save_as(path)
        path.with_suffix(".json").write_text(json.dumps(st["script"], ensure_ascii=False, indent=2), encoding="utf-8")
        path.with_suffix(".txt").write_text(st["sources"], encoding="utf-8")
        print("保存:", path)
        await browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
