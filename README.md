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

Videos play from their first story: a new video, a new story length or layout, and coming back to the page (from another app, another tab or the lock screen) all start from the top. Pause and Play, and the seek bar, stay where they are. The same holds on Humor and the Japanese page.

* opens Settings. The device name (Phone, X, YouTube, or PC) is there, with the country, the language, and the X account.

- **Layout** follows the device until you choose Phone, X, YouTube, or PC.
- **Country** is Japan or the United States. **Language** is English, Japanese, or both. Changing the country sets Japan to both and the United States to English.
- **Accounts with replies and comments**, for example `@name`: News plays no replies, except for the accounts added here. Their posts play with the replies and comments under them, up to half of a video. **Send to githito.xapi** opens a GitHub issue titled `account` with the list; after Submit, githito.xapi reads those accounts' replies from its next run (every half hour). The note under the button says which accounts githito.xapi already reads. Opening the page from X adds no account; `?x=name` does.
- Choices stay in this browser. The next visit collects again.

```bash
python run.py --country JP --lang ja
python run.py --x-user name --country US --lang en
```

Wallpaper, under the picture: Morning is the original picture. Evening is warmer, Night is darker, and Pop is brighter.

Music, under the picture: **1**, **2** and **3**, each 8 bars (1 and 3 at 90 BPM, 21.3 seconds; 2 at 110 BPM,
17.5 seconds), made from the MIDI files `assets/midi/1.mid`, `2.mid` and `3.mid`. 1 plays first. The music plays on its own and is not tied to
the video: it repeats without a seam, and a new video, Update, the video's own repeat, the seek bar, the story
length and exporting leave it playing where it is. On News and the Japanese page Pause stops it; on Humor
the Sound button turns it off and on. Humor has the same three songs; the Japanese page plays 1.

## Where the news comes from

**In Japan the News page's source is X.** [githito.xapi](https://github.com/Githitosh/githito.xapi) collects it
ahead of time (`news.mjs`, every hour, kept for three days) and the page reads one file, `v1/news-ja.json`, so a video starts
in about a second and Update answers at once.

- **Headlines, no replies**: every card is a headline from a news account on X. There is no switch for
  replies any more: they made room for abuse.
- **Replies only for the accounts added in Settings** (Accounts with replies and comments): up to half of
  a video is their posts and the earnest replies under them, a small line under each reply saying which
  post it answers. githito.xapi reads replies only for the accounts sent to it, and keeps only earnest
  ones (no insults, blame, mockery, politics or grave news). A post of an account that is not a news
  account plays only for a reader who added it.
- A genre chip plays that genre's headlines.
- **Sources**: X only, unless the web or a paper from abroad is switched on in Settings. A genre keeps to
  these switches (it used to read web feeds whatever they said).
- **Add a medium, a website or a keyword** (Settings): type a company name, a medium or `example.com`, press
  Search, and add what was found. Its news is searched on the web (Google News and Bing News) and plays
  first in every video, up to half of it. Up to eight can be added.
- **What plays is chosen by githito.xapi, at random**, after every hourly collection (the `play` orders in
  its files). The pages only read an order from the top, leaving out what the reader has already seen;
  they do no searching and no choosing of their own for this. The same holds for Humor's romance stories
  (one order each for the morning, the day and the night).
- With another edition, or with a lineup line that is not a genre, the page searches as described below. There is no pull down to refresh. Update makes a new video.

The searches the page makes itself:

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
- Humor's romance stories are prepared ahead of time by
  [githito.xapi](https://github.com/Githitosh/githito.xapi) (`humor.mjs`, every hour, kept for three days) and read
  from `v1/humor-ja.json`, so the first video and Update start in about a second. Loving talk comes
  first; in the morning (4 to 11) good mornings are seven in ten. When every story has played, the
  one that played longest ago comes back first. With other genres in the lineup, or
  when the file cannot be read, the page searches live as before.

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
| `assets/` | Five backgrounds, the songs (`song_1.m4a`, `song_2.m4a`, `song_3.m4a`, from `midi/1.mid`, `2.mid`, `3.mid`) and an older recording no page plays (`sandman_1920.m4a`) |
| `song.py` | Makes `assets/song_1.m4a`, `song_2.m4a` and `song_3.m4a` from the MIDI files |
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
- The chosen song is copied into the MP4 as it is, from its beginning, and repeats to the end of the video. Each file holds the 8 bars twice (a whole number of AAC frames each: 1000 for 1 and 3, 818 for 2); past its end the frames are taken again from one song length earlier, so the repeat has no seam.

## Credits

- Songs 1, 2 and 3: the MIDI files in `assets/midi/`, played with FluidSynth and the FluidR3 GM SoundFont (MIT License): Chords on a piano, Bass on a fingered bass, Drums on the drum channel. `python song.py` makes the files again; loudness is about -16 LUFS.
- The Japanese Sandman: Paul Whiteman and His Ambassador Orchestra, August 19, 1920, Wikimedia Commons. Public domain. The excerpt starts at 0:12.
- Photos: U.S. National Park Service and NOAA (Glacier, Yellowstone, Lake Mead, southeast Alaska). Public domain.
- Coffee-break background: an image made with Grok.
- News lines are short summaries. Read the script before publishing it.
