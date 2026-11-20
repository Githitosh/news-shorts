# News Shorts

Open the page and it creates a news video from today's headlines, then plays it. A tap or click on the picture pauses the video, and the next one plays it again, on News and on Reply News. The music is on, and the page opens with Music 1 (another song chosen in Settings plays until the page is closed). A browser lets a page make sound only after a tap, so the music starts at the first tap, wherever it lands: on the Music button that tap does not switch the music off, and on the picture it does not pause; it only starts the sound. The **Music** button under the video is lit while the music is on; press it and the music stops and the light goes out (the choice is kept, and a video downloaded then has no music). The button with the arrow (⬇️) makes the video an MP4 and then hands it over: on a phone the system's share sheet opens with the file in it (Save Video, LINE, X…), as after any download. A browser opens that sheet only right after a tap, and making the MP4 takes longer, so when it refuses a panel comes up (The video is ready) whose one button opens the sheet. On a computer the file is downloaded and the panel offers X and LINE for the page's link. The first word on each story is taken from that story. **Update** collects a new edition: the button says Creating… until the new video starts. Pull down at the top does the same. No API key. The picture keeps the original text size. Sources stay on the small credit line. Settings are behind the * button. Press a genre there, or write a lineup such as `Musk X, 3`. Each line is a request and a count. The first line opens the video. Genres are Space, Politics, Science, Culture, Local, Entertainment, Public safety, Sports, Food, and Restaurant. Each one can sit at the Top, Middle, or Bottom. Hide violent crime is on. Uncheck a source to leave it out.

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
- **Country** is Japan or the United States. **Language** is English, Japanese, or Both. English writes the cards in English only and Japanese in Japanese only; only Both writes the two on one card (the English headline large, the Japanese lines under it). Japan starts with Japanese and the United States with English; Both is there to be chosen. (For a day a saved choice of Japanese was moved to Both; it is moved back once.)
- **Reply request** (the field under the video), for example `@name`: News plays no replies, except for the accounts added here. Their posts play with the replies and comments under them, up to half of a video. **Send to githito.xapi** opens a GitHub issue titled `account` with the list; after Submit, githito.xapi reads those accounts' replies from its next run (every half hour). The note under the button says which accounts githito.xapi already reads. Opening the page from X adds no account; `?x=name` does.
- Choices stay in this browser. The next visit collects again.

```bash
python run.py --country JP --lang ja
python run.py --x-user name --country US --lang en
```

Wallpaper, under the picture: Morning is the original picture. Evening is warmer, Night is darker, and Pop is brighter. Both pages start with Morning, the dark picture (Reply News used to start with Day, the light one; a saved Day is moved to Morning once, and Day can be chosen again).

Music, under the picture: **1**, **2** and **3**, each 8 bars (1 and 3 at 90 BPM, 21.3 seconds; 2 at 110 BPM,
17.5 seconds), made from the MIDI files `assets/midi/1.mid`, `2.mid` and `3.mid`. 1 plays first. The music plays on its own and is not tied to
the video: it repeats without a gap (it plays through Web Audio, `src/music.js`, which repeats one song length of the
decoded file sample for sample; an audio element stopped for a moment at each repeat), and a new video, Update, the video's own repeat, the seek bar, the story
length and exporting leave it playing where it is. On News Pause stops it; on Humor
the Music button turns it off and on, as on News. Humor has the same three songs. Reply News reads githito.xapi's stories whatever Language says: Japanese shows them as written (the corner says 恋愛), English puts their words into English on the cards.

## The pages read githito.xapi only

The pages ask X nothing themselves: News and Reply News (the page at `humor/`, formerly called Humor) play
what [githito.xapi](https://github.com/Githitosh/githito.xapi) collected. Whatever in the pages used to ask
FxTwitter, Bluesky or X's own pages gets nothing now, the "X posts" feed is gone from the News settings, and
on Reply News every lineup plays the prepared stories. The terms of use are in `terms.html`, linked at the
foot of both pages.

News reads githito.xapi whatever **Country** is chosen. (It used to read it for Japan only: with the United
States chosen it searched the web instead, and when the web did not answer it played the sample of Nov 14,
again and again, with this page's own address as the link.) The page's own words are English only when
**Language** is English. When the page's own search fails, or finds nothing and no video is there to keep
playing, the news githito.xapi holds plays instead. The sample never plays in the place of the news: when no
news can be read at all, the page says so and tries again every quarter of a minute.

**Never shown, whatever the switches say** (`src/never.js`, the same three lists as githito.xapi's
`filters.mjs`; change the two together): cruel news (killing, bodies, torture, sexual violence, abuse,
suicide, violence that reached children); news that touches one person's honour or private life (an
arrest, a suspect, a charge, a sentence; an allegation, an exposure, an affair, a pile-on); and slander in
what people write themselves, in replies and in the Reply News stories (insults, slurs, threats, charges
against a person, anything pointing at where somebody lives or works). githito.xapi leaves these out when
it collects; the pages sift what they read once more, so a change holds at once and an older file's
contents do not play. "Turn violence off" in Settings is a further, wider switch.

Before a video shows, the picture says **SEARCHING News**: on opening the page until the first video, and
after Update or at the end of a video when the next one takes more than half a second. A translator that
does not answer holds a video back eight seconds at most.

## Where the news comes from

**In Japan the News page's source is X.** [githito.xapi](https://github.com/Githitosh/githito.xapi) collects it
ahead of time (`news.mjs`, every half hour, kept for three days) and the page reads one file, `v1/news-ja.json`, so a video starts
in about a second and Update answers at once.

- **Headlines, no replies**: every card is a headline from a news account on X. There is no switch for
  replies any more: they made room for abuse.
- **A card looks as in the first News videos**: it opens on an English keyword, then shows the English
  headline large with the rest of it under, the Japanese lines below, and a few tags at the foot.
  githito.xapi sends each headline's English with it (and one more line of the post when there is one);
  for a headline that has none yet the page asks for the translation itself, and without it the card is
  Japanese only.
- **Replies only for the accounts added under the video** (Reply request: the field and Add are on the main screen, under the video, on News and on Reply News, and the list is one for the two pages. Add alone sends the list to githito.xapi: GitHub opens with the request written, and Submit there sends it; there is no separate send button. On Reply News only the replies to an added account's posts play, a card each, first in a video and up to half of it, marked リプライ in the corner; the account's own posts do not play there, which would make the page read like News. No line of small print sits under the accounts on either page): up to half of
  a video is their posts and the earnest replies under them, a small line under each reply saying which
  post it answers. githito.xapi reads replies only for the accounts sent to it, and keeps only earnest
  ones (no insults, blame, mockery, politics or grave news). A post of an account that is not a news
  account plays only for a reader who added it.
- A genre chip plays that genre's headlines.
- **Sources**: X only (the news githito.xapi collects there). Nothing is read from the web, and **no
  Japanese medium is read by RSS**: the web source (Google News, Bing News, Yahoo! News' topic feeds, NPR)
  is gone from the page, and so is the old page at `ja/`, which read NHK's and Asahi's RSS (its address now
  opens News with Japanese cards). The papers from abroad (BBC, ABC, Reuters) are still switches: they play
  when they are switched on and X is switched off.
- **Add a medium or a keyword** (Settings): type a medium's name or a word (a company's name, say), press
  Search, and add what was found. It is looked for in the news githito.xapi collected from X, by the
  account's name and by the words of the headline, not on the web, and plays first in every video, up to
  half of it. Up to eight can be added. A medium githito.xapi does not read yet is added by its X account
  under Accounts and sent to githito.xapi.
- **Words in the lineup** (a line that is no genre) are looked for in the same news from X.
- **What plays is chosen by githito.xapi, at random**, after every hourly collection (the `play` orders in
  its files). The pages only read an order from the top, leaving out what the reader has already seen;
  they do no searching and no choosing of their own for this. The same holds for Humor's romance stories
  (one order each for the morning, the day and the night).
- There is no pull down to refresh. Update makes a new video.

**The cards and the wide page.** With Language on Both a card has the English first (the headline, large)
and the Japanese after it; on the wide page (PC) the English is on the left and the Japanese on the right,
with no line between them. A card in one language (Japanese only, English only) is one block in the middle
of the wide page.

The searches the page makes itself (only with X switched off and a paper from abroad switched on):

No API key. The page reads the papers' public feeds through more than one relay, so that one of them refusing or being slow does not stop the video.

| Paper | How it is read |
|---|---|
| BBC, ABC | their own RSS (English), translated by the page |
| Reuters | a news search limited to reuters.com |

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
| `src/never.js` | What the pages never show: cruel news, news on a person's honour or private life, slander (the same lists as githito.xapi's `filters.mjs`) |
| `src/music.js` | The music player: the song repeated without a gap (Web Audio), for News and Humor |
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
- **Speed-read news.** A headline card in one language says what happened on its second beat and who on its third (`twoJapanese`, `whoOf` in `src/app.html`). The "who" is read from the headline as the papers write one: a person where a phrase starts (a full name, a name with a title such as 高市首相 or 田嶋幸三氏, names joined by ＆ or ×, whoever stands right before what was said), or the office, court or survey the news comes from at its end (…―国交省, … 内閣府調査). The second beat is the headline without that name; of a long one, its first part. A headline that names nobody is shown in its two parts; one too short to cut is shown whole, and the third beat is the line the post added, or the paper that wrote it. A short headline is not cut in two. `whoOf` answers nothing when it is not sure: a wrong word in the place of a name is worse than no name.
- A card in one language (Language: Japanese, or English) shows one sentence in two beats: its first part at 0.77 seconds and its second at 1.57 seconds, in the same letters and the same size, with nothing small under them and no tags. The cut is where the sentence turns (`cutJa`, `cutEn` in `src/engine.js`): after a mark, a space or a bracket, near the middle. A headline that does not turn anywhere takes the line its post added as the second part, or is cut all the same at the least costly place, so the third beat always has words of its own. In English each part is the translation of that part of the Japanese (the two are asked for as two lines).
- The lines of such a card end where a phrase ends (`fitter`, `breakCost`): after a mark or a particle, not inside a word or a quotation when that can be helped, and each card is written as large as it fits (`twinLayout`): from the largest letters down to the first size at which its lines fit the width and its two parts fit the box, a part taking up to six lines, then a little smaller when that buys better line ends. A short card is large and a long one smaller; one long card does not make the others small. (Cards with both languages keep one size for the video.)
- A headline githito.xapi cut short (older ones stop after 45 characters and …) loses its broken last word on the page (`wholeLine`); ruled lines such as ╋━━━╋ are not words and are left out.
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
