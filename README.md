# News Shorts

Open the page and the news video plays. The layout follows the device: YouTube, X, a phone, or a PC. Four public-domain recordings can be selected under the picture.

| Device | Picture | When it is chosen |
|---|---|---|
| **Phone** | Portrait 1080×1920 | A phone browser. Text uses the full width. |
| **X** | Portrait 1080×1920 | The X app. Same full-width layout as Phone. |
| **YouTube** | Portrait 1080×1920 | The YouTube app. The right and bottom stay clear for buttons. |
| **PC** | Landscape 1920×1080 | A computer. The headline is on the left and the Japanese text is on the right. |

https://githitosh.github.io/news-shorts/

GitHub Pages serves the root of `main`. The picture starts on its own. Safari blocks the sound until the picture is tapped once. The video is the November 14, 2026 edition: 13 stories, about 42 seconds, then it repeats.

Country, language, and X are under the picture.

- **Country** chooses which country's news is collected. **Language** is the language of the lines under the English headline. Changing the country sets its usual language. You can change the language after that.
- **X account** is the account to link, for example `@name`. **Make video from follows** reads recent posts and replies from accounts that account follows, keeps the ones about the selected country, and plays a new video in the selected language. This uses the saved API key. With no key yet, the page asks for one. A linked account is saved only in this browser.
- On the next visit, a linked account and a saved key make the video again when the page opens.

```bash
python run.py --x-user name --country US --lang en
python run.py --country FR --lang fr --provider claude
```

Music, under the picture:

| Button | Recording |
|---|---|
| Jupiter | Holst, “Jupiter”, London Symphony Orchestra, Columbia, 1922–23 |
| Neptune | Holst, “Neptune”, same recording, 1923 |
| Stars and Stripes | Sousa’s Band, Edison, 1909 |
| Sandman | Paul Whiteman and His Ambassador Orchestra, 1920 |

## Make a new video

`index.html` contains the pictures, the music, and the program. Chrome, Edge, and Safari can open it.

Add `?edit=1` to show the tools:

1. Open **Settings**, choose Grok or Claude, and enter an API key. The key stays in this browser.
   - **Grok** searches X and the web (an xAI key).
   - **Claude** searches the web (an Anthropic key).
2. Choose **Collect news and make the video**. Collection, the coffee break, and export run on their own.
3. Edit the script under **Script (JSON)**, then **Apply script** and **Export MP4**. **Sample (Nov 14)** reloads the original script.

On a phone, Share → Add to Home Screen opens it full screen.

## Run without a window

Use this when the browser cannot call the API, or when the video should be made on a schedule.

```bash
pip install playwright && python -m playwright install chromium
export XAI_API_KEY=...        # Grok. For Claude, set ANTHROPIC_API_KEY
python run.py                 # save today's video in out/, plus the script .json and sources .txt
python run.py --date 2026-11-14 --provider claude
python run.py --sample        # export the sample script, no API call
python run.py --formats x     # one format: x, youtube, or pc
```

## Files

| Path | What it is |
|---|---|
| `index.html` | The page. `build.py` writes it. |
| `manifest.webmanifest`, `*.png` | Name and icons for Add to Home Screen |
| `run.py` | Runs `index.html` without a window and saves the MP4 files |
| `src/engine.js` | Drawing for the three layouts |
| `src/app.html` | The page, news collection, the coffee break, and MP4 export |
| `assets/` | Five backgrounds and four music files |
| `samples/2026-11-14.json` | The original script |
| `lib/mp4-muxer.js` | MP4 library (MIT) |
| `build.py` | Rebuilds `index.html` from `src/` and `assets/` |

Rebuild after changing `src/` or `assets/`:

```bash
python build.py
```

## Timing

- Each story is 3.2 seconds: a large keyword, then the headline at 0.77 seconds, Japanese at 1.57 seconds, and tags at 2.37 seconds.
- The background eases in by 2.2% over those 3.2 seconds. The order is A B C C A B D C D C B D. The coffee break uses the study picture.
- English headlines use a heavy serif, condensed. Small words such as to, and, and of stay small.
- Text bounds: Phone and X use 60px side margins, YouTube uses 60–900px, and PC uses 120–1800px.
- On Phone, X, and PC, English line breaks are chosen automatically. A Japanese `／` becomes a line break only when the line does not fit.
- The selected music file is copied into the MP4 as it is. If the video is shorter than the recording, playback starts late enough to finish with the recording.

## Credits

- Jupiter and Neptune: Holst conducting the London Symphony Orchestra (Columbia, 1922–23), from Wikimedia Commons “Holst - The Planets (Columbia 1922-23).flac”. Jupiter is the 41.6 seconds starting at 18:21. Neptune is 41.6 seconds starting at 0:45 of the Neptune excerpt. Clicks and hiss were reduced with ffmpeg `adeclick` and `afftdn`, and loudness was set to -16 LUFS. The music and the recordings are in the public domain.
- Stars and Stripes Forever: Sousa’s Band for Edison Records, November 1909, Wikimedia Commons. Public domain. The excerpt starts at 0:18.
- The Japanese Sandman: Paul Whiteman and His Ambassador Orchestra, August 19, 1920, Wikimedia Commons. Public domain. The excerpt starts at 0:12.
- Photos: U.S. National Park Service and NOAA (Glacier, Yellowstone, Lake Mead, southeast Alaska). Public domain.
- Coffee-break background: an image made with Grok.
- News lines are short summaries. Read the script before publishing it.
