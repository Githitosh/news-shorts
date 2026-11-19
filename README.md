# News Shorts

Open the page and it creates a news video from today's headlines, then plays it. Tap the picture once for sound. The first word on each story is taken from that story. **Update** collects a new edition: the button says Creating… until the new video starts. Pull down at the top does the same. No API key. The picture keeps the original text size. Sources stay on the small credit line. Settings are behind the * button. Press a genre there, or write a lineup such as `Musk X, 3`. Each line is a request and a count. The first line opens the video. Genres are Space, Politics, Science, Culture, Local, Entertainment, Public safety, Sports, Food, and Restaurant. Each one can sit at the Top, Middle, or Bottom. Hide violent crime is on. Uncheck a source to leave it out.

| Device | Picture | When it is chosen |
|---|---|---|
| **Phone** | Portrait 1080×1920 | A phone browser. Text uses the full width. |
| **X** | Portrait 1080×1920 | The X app. Same full-width layout as Phone. |
| **YouTube** | Portrait 1080×1920 | The YouTube app. The right and bottom stay clear for buttons. |
| **PC** | Landscape 1920×1080 | A computer. The headline is on the left and the news text is on the right. |

https://githitosh.github.io/news-shorts/

GitHub Pages serves the root of `main`. The picture starts on its own. Safari blocks the sound until the picture is tapped once. The video is the November 14, 2026 edition: 13 stories, about 42 seconds, then it repeats.

* opens Settings. The device name (Phone, X, YouTube, or PC) is there, with the country, the language, and the X account.

- **Layout** follows the device until you choose Phone, X, YouTube, or PC.
- **Country** is Japan or the United States. **Language** is English, Japanese, or both. Changing the country sets Japan to both and the United States to English.
- **X account**, for example `@name`, adds recent posts and replies from accounts that account follows. No API key. Opening the page from that account on X fills the name in, and the next visit collects again.
- Choices stay in this browser. The next visit collects again.

```bash
python run.py --country JP --lang ja
python run.py --x-user name --country US --lang en
```

Wallpaper, under the picture: Morning is the original picture. Evening is warmer, Night is darker, and Pop is brighter.

Music, under the picture:

| Button | Recording |
|---|---|
| Jupiter | Holst, “Jupiter”, London Symphony Orchestra, Columbia, 1922–23 |
| Neptune | Holst, “Neptune”, same recording, 1923 |
| Stars and Stripes | Sousa’s Band, Edison, 1909 |
| Sandman | Paul Whiteman and His Ambassador Orchestra, 1920 |

## Where the news comes from

No API key. The page reads public feeds, from more than one source and through more than one relay, so that one of them refusing or being slow does not stop the video.

| Edition | Front pages | A genre |
|---|---|---|
| Japan | Google News, Yahoo! News (its main topics and one section in turn), and one paper from abroad in turn (BBC, ABC, Reuters) | Yahoo! News' topic page where it has one, a search of Google News and of Bing News, and the BBC's section |
| United States | Google News, NPR, and BBC, ABC or Reuters in turn | A search of Google News and of Bing News, and the BBC's section |

- In Japan seven stories in ten are the edition's own; elsewhere half.
- A feed cannot be read by a page directly, so it goes through a relay: rss2json, allorigins or r.jina.ai. Each refuses some sites (r.jina.ai refuses Google News at times, rss2json cannot read Yahoo! News, allorigins cannot read Google News), so for each site the relay that reads it best is asked first and the next one takes over when it fails or does not answer in two and a half seconds. A relay that failed for a site rests for ten minutes.
- What a feed returned is kept for four minutes, so pressing Update again does not ask for the same page.
- GDELT is asked last, only when the others are short: it is slow and often refuses.
- Press releases, blog platforms and stories in a script the edition does not read are left out.
- Humor reads its news the same way (the topics its jokes are about).

## Make a new video

`index.html` contains the pictures, the music, and the program. Chrome, Edge, and Safari can open it. Collection uses public headlines, so there is no API key.

* opens the tools:

1. Choose the country and the language, then **Collect and play**.
2. Edit the script under **Script (JSON)**, then **Apply script** and **Export MP4**. **Sample (Nov 14)** reloads the original script.
3. **Export MP4 files after the stories are ready** saves Phone, YouTube, and PC files.

On a phone, Share → Add to Home Screen opens it full screen.

## Run without a window

```bash
pip install playwright && python -m playwright install chromium
python run.py                 # save today's video in out/, plus the script .json and sources .txt
python run.py --country JP --lang ja
python run.py --sample        # export the sample script
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

- Each story is 3.2 seconds: a large keyword, then the headline at 0.77 seconds, the news lines at 1.57 seconds, and tags at 2.37 seconds.
- The background eases in by 2.2% over those 3.2 seconds. The order is A B C C A B D C D C B D. The coffee break uses the study picture.
- English headlines use a heavy serif, condensed. Small words such as to, and, and of stay small.
- Text bounds: Phone and X use 60px side margins, YouTube uses 60–900px, and PC uses 120–1800px.
- On Phone, X, and PC, English line breaks are chosen automatically. A `／` in the news lines becomes a line break only when the line does not fit.
- The selected music file is copied into the MP4 as it is. If the video is shorter than the recording, playback starts late enough to finish with the recording.

## Credits

- Jupiter and Neptune: Holst conducting the London Symphony Orchestra (Columbia, 1922–23), from Wikimedia Commons “Holst - The Planets (Columbia 1922-23).flac”. Jupiter is the 41.6 seconds starting at 18:21. Neptune is 41.6 seconds starting at 0:45 of the Neptune excerpt. Clicks and hiss were reduced with ffmpeg `adeclick` and `afftdn`, and loudness was set to -16 LUFS. The music and the recordings are in the public domain.
- Stars and Stripes Forever: Sousa’s Band for Edison Records, November 1909, Wikimedia Commons. Public domain. The excerpt starts at 0:18.
- The Japanese Sandman: Paul Whiteman and His Ambassador Orchestra, August 19, 1920, Wikimedia Commons. Public domain. The excerpt starts at 0:12.
- Photos: U.S. National Park Service and NOAA (Glacier, Yellowstone, Lake Mead, southeast Alaska). Public domain.
- Coffee-break background: an image made with Grok.
- News lines are short summaries. Read the script before publishing it.
