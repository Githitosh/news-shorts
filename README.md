# News Shorts（ニュース動画の自動生成）

2026年11月14日の「News Shorts」と同じ形の縦型動画（1080×1920・30fps・41.6秒）を、HTML だけで作ります。

```
X とウェブからニュースを12本集める（Grok か Claude）
  → コーヒーブレイクを自動で書く
  → 1本3.2秒 × 13本の映像を描く（大きなキーワード → 見出し → 日本語 → タグ）
  → 音楽（Holst 指揮の「Jupiter」1922–23年の録音）を付けて MP4 に書き出す
```

## 使い方

### ブラウザで

1. `index.html` を開く（これ1つで動きます。写真・音楽・プログラムは中に入っています。パソコンなら Chrome・Edge・Safari で開けます）
2. 「設定」で AI を選び、API キーを入れる
   - **Grok**：X の投稿を直接検索します（xAI の API キー）
   - **Claude**：ウェブを検索します（Anthropic の API キー）
   - キーはその端末のブラウザにだけ保存されます
3. 「ニュースを集めて動画にする」を押す → 集める・書く・書き出すまで自動で進み、「MP4を保存」が出ます

「台本（JSON）」で見出しや文を直して「台本を反映」→「MP4を書き出す」で作り直せます。「見本（11/14）」で元の動画の台本を読み込めます。

### 自動実行（画面なし）

ブラウザから API に直接つながらないときや、決まった時刻に作りたいときに使います。

```bash
pip install playwright && python -m playwright install chromium
export XAI_API_KEY=...        # Grok のとき（Claude なら ANTHROPIC_API_KEY）
python run.py                 # 今日の動画を out/ に保存（台本 .json と出典 .txt も）
python run.py --date 2026-11-14 --provider claude
python run.py --sample        # 見本の台本で書き出すだけ（API なし）
```

## 中身

| 場所 | 内容 |
|---|---|
| `index.html` | 本体（`build.py` で作ったもの） |
| `run.py` | 画面なしで index.html を動かし、MP4 を保存する |
| `src/engine.js` | 描画（配置・大きさ・切り替えのタイミング） |
| `src/app.html` | 画面、ニュース集め、コーヒーブレイク、MP4 書き出し |
| `assets/` | 背景5枚（元の動画から取り出したもの）と音楽（1922–23年の録音から切り出し、ノイズを除いたもの） |
| `samples/2026-11-14.json` | 元の動画の台本 |
| `lib/mp4-muxer.js` | MP4 を組み立てるライブラリ（MIT） |
| `build.py` | `src/` と `assets/` から `index.html` を作り直す |

## 動画の決まり（元の動画から測った値）

- 1本3.2秒。0〜0.77秒は大きなキーワード、0.77秒から0.2秒で見出しに切り替え、1.57秒から日本語、2.37秒からタグ
- 背景は3.2秒で2.2%ゆっくり寄る。並びは A B C C A B D C D C B D、最後のコーヒーブレイクは書斎の画像
- 英語の見出しは明朝の極太を横に縮めたもの。副見出しの to / and / of などは小さく出る
- 文字は画面の左から60〜900pxの範囲（右側は YouTube のボタンの位置なので空けてある）
- 音楽は `assets/jupiter_1922.m4a` の音をそのまま入れる（作り直さない）。本数が少ないときは、曲の終わりに合わせて途中から始める

## 出典・権利

- 音楽：Holst「Jupiter」Holst 指揮 London Symphony Orchestra（Columbia, 1922–23 の録音）、Wikimedia Commons「Holst - The Planets (Columbia 1922-23).flac」の 18:21 から 41.6 秒
  - 1923年に発売された録音で、曲・録音ともパブリックドメイン
  - クリックとヒスノイズを除き（ffmpeg の adeclick・afftdn）、音量を -16 LUFS にそろえた
- 写真：U.S. National Park Service・NOAA（Glacier, Yellowstone, Lake Mead, SE Alaska）、パブリックドメイン
- コーヒーブレイクの背景：AI で作った画像（Grok）
- ニュースの文は AI が投稿や記事をもとに短くまとめます。公開する前に台本を確認してください
