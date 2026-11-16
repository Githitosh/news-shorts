/* News Shorts — 描画エンジン（1080×1920、30fps、1本3.2秒） */
(function (global) {
'use strict';

const W = 1080, H = 1920, FPS = 30, DUR = 3.2;
const INK = '#F5F1E9';
const F_SERIF = '"Noto Serif JP","Noto Serif CJK JP","Source Han Serif JP","Hiragino Mincho ProN","Yu Mincho",serif';
const F_TIMES = '"Tinos","Liberation Serif","Times New Roman",Times,serif';
const F_SANS = '"Noto Sans JP","Noto Sans CJK JP","Source Han Sans JP","Hiragino Sans","Yu Gothic",sans-serif';

/* 位置と大きさ（元の動画から測った値） */
const P = {
  left: 60, right: 900, cx: 480,
  header: { base: 241, size: 42, w: 600, sx: 0.742, cx: 477 },
  cat: { base: 304, size: 40, w: 700, sx: 0.965, right: 896 },
  rule: 3,
  rule1: 326, rule2: 1364,
  box: { top: 368, bottom: 1256, center: 812 },
  head: { sx: 0.608, lh: 0.935, max: [257, 200, 160, 130], maxW: 800, cap: 0.743, topPad: 0.139 },
  sub: { sx: 0.60, lh: 0.935, ratio: 0.52, ratioW: 0.52, max: 145, maxW: 835, small: 0.62 },
  gap: { headRule: [8, 0.103], ruleSub: [21.4, 0.18], subShort: [16, 0.09], shortJp: 35 },
  short: { w: 240 },
  jp: { size: 68, sx: 0.695, w: 900, line: 80, para: 107.5, maxW: 850, ascent: 0.86, inkH: 64 },
  tags: { base: 1339.5, size: 42.7, w: 700, gap: 43, sx: 0.85 },
  foot: { base: 1417, size: 41, w: 600, sx: 0.77, page: 40, psx: 0.965 },
  credit: { base1: 1460, base2: 1492, size: 20, maxW: 800, maxW1: 840, color: 'rgba(245,241,233,0.56)' },
  kw: { sx: 0.276, maxH: 891, cy: 818, w: 840 },
  zoom: 0.022,
  fade: 0.2, t1: 23 / 30, t2: 47 / 30, t3: 71 / 30,
};

const BG_ORDER = ['A', 'B', 'C', 'C', 'A', 'B', 'D', 'C', 'D', 'C', 'B', 'D'];
const CREDIT_MUSIC = 'Music: Holst ‘Jupiter’ – Holst / London Symphony Orchestra (Columbia, 1922–23), Wikimedia Commons';
const CREDIT_PHOTO = 'Photos: U.S. National Park Service & NOAA (Glacier, Yellowstone, Lake Mead, SE Alaska), public domain';
const CREDIT_COFFEE = 'Background: AI-generated image (Karuizawa-style study), Grok Bot';

const mcv = document.createElement('canvas');
const mctx = mcv.getContext('2d');
function font(w, size, fam) { return `${w} ${size}px ${fam}`; }
function adv(text, f) { mctx.font = f; return mctx.measureText(text).width; }
function ink(text, f) {
  mctx.font = f; const m = mctx.measureText(text);
  return { l: m.actualBoundingBoxLeft, r: m.actualBoundingBoxRight, a: m.actualBoundingBoxAscent, d: m.actualBoundingBoxDescent, w: m.width };
}
const smooth = (a, b, t) => { const x = Math.min(1, Math.max(0, (t - a) / (b - a))); return x * x * (3 - 2 * x); };
const pad2 = n => String(n).padStart(2, '0');

/* 小さく出す語（台本で小文字にした語） */
function tokens(line) {
  return line.split(/(\s+)/).filter(s => s.length).map(s => ({ t: /^\s+$/.test(s) ? ' ' : s, small: /^[a-z][a-z'’.-]*$/.test(s) }));
}
function subWidth(line, size) {
  let w = 0;
  for (const k of tokens(line)) {
    const s = k.small ? size * P.sub.small : size;
    w += adv(k.small ? k.t.toUpperCase() : k.t, font(900, s, F_SERIF));
  }
  return w * P.sub.sx;
}

/* 日本語の行：「／」か改行で区切る。長すぎる行は文節で折り返す */
function jpWidth(t) { return adv(t, font(P.jp.w, P.jp.size, F_SERIF)) * P.jp.sx; }
const NO_START = '、。，．・：；？！ー）」』】〕”’ぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮヵヶ々〜…‥%％';
const NO_END = '（「『【〔“‘';
function wrapJp(text) {
  const parts = String(text).split(/[／\n]/).map(s => s.trim()).filter(Boolean);
  const out = [];
  for (const p of parts) {
    if (jpWidth(p) <= P.jp.maxW) { out.push(p); continue; }
    out.push(...splitBalanced(p));
  }
  return out;
}
function breakPoints(s) {
  let segs = null;
  try {
    if (Intl.Segmenter) segs = [...new Intl.Segmenter('ja', { granularity: 'word' }).segment(s)].map(x => x.index);
  } catch (e) { segs = null; }
  const pts = new Set();
  if (segs) segs.forEach(i => { if (i > 0) pts.add(i); });
  else for (let i = 1; i < s.length; i++) pts.add(i);
  for (let i = 1; i < s.length; i++) if (s[i - 1] === ' ' || s[i - 1] === '　') pts.add(i);
  return [...pts].filter(i => !NO_START.includes(s[i]) && !NO_END.includes(s[i - 1]) &&
    !(/[0-9A-Za-z]/.test(s[i - 1]) && /[0-9A-Za-z.,]/.test(s[i]))).sort((a, b) => a - b);
}
function splitBalanced(s) {
  const pts = breakPoints(s);
  let best = null;
  for (const i of pts) {
    const a = s.slice(0, i).trim(), b = s.slice(i).trim();
    const wa = jpWidth(a), wb = jpWidth(b);
    if (wa > P.jp.maxW) continue;
    const particle = /[のがをにはでとへもや、]$/.test(a) ? -40 : 0;
    const score = Math.max(wa, wb) + particle;
    if (!best || score < best.score) best = { score, a, b, wb };
  }
  if (!best) { const h = Math.ceil(s.length / 2); return [s.slice(0, h), ...splitBalanced(s.slice(h))].filter(Boolean); }
  return best.wb > P.jp.maxW ? [best.a, ...splitBalanced(best.b)] : [best.a, best.b];
}

/* 1本分の配置を決める */
function layout(it) {
  const head = (it.head && it.head.length ? it.head : [it.kw]).map(s => String(s).toUpperCase());
  const sub = (it.sub || []).map(String);
  const n = head.length;
  const hMax = P.head.max[Math.min(n, P.head.max.length) - 1];
  const hw = Math.max(...head.map(l => adv(l, font(900, 100, F_SERIF)))) * P.head.sx / 100;
  const sh0 = Math.min(hMax, P.head.maxW / hw);
  const ratio = P.head.maxW / hw < hMax ? P.sub.ratioW : P.sub.ratio;
  const sw = sub.length ? Math.max(...sub.map(l => subWidth(l, 100))) / 100 : 1;
  const ssLim = Math.min(P.sub.max, P.sub.maxW / sw);
  const jp = [];
  (it.jp || []).forEach((p, pi) => wrapJp(p).forEach((t, li) => jp.push({ t, para: li === 0 && pi > 0 })));

  function place(f) {
    const Sh = sh0 * f, Ss = Math.min(ssLim, ratio * sh0) * f;
    let y = 0;
    const L = { Sh, Ss, head: [], sub: [], jp: [] };
    const capTop0 = y + P.head.topPad * Sh;
    head.forEach((t, i) => L.head.push({ t, base: capTop0 + P.head.cap * Sh + i * P.head.lh * Sh }));
    let last = L.head[L.head.length - 1].base;
    L.rule = last + P.gap.headRule[0] + P.gap.headRule[1] * Sh;
    if (sub.length) {
      const sc0 = L.rule + P.gap.ruleSub[0] + P.gap.ruleSub[1] * Ss;
      sub.forEach((t, j) => L.sub.push({ t, base: sc0 + P.head.cap * Ss + j * P.sub.lh * Ss }));
      last = L.sub[L.sub.length - 1].base;
      L.short = last + P.gap.subShort[0] + P.gap.subShort[1] * Ss;
    } else L.short = L.rule + 24;
    let jt = L.short + P.gap.shortJp;
    jp.forEach((l, k) => {
      if (k > 0) jt += l.para ? P.jp.para : P.jp.line;
      L.jp.push({ t: l.t, base: jt + P.jp.ascent * P.jp.size });
    });
    L.bottom = jp.length ? jt + P.jp.inkH : L.short + 3;
    return L;
  }
  const avail = P.box.bottom - P.box.top;
  let L = place(1), f = 1;
  if (L.bottom > avail) {
    let lo = 0.2, hi = 1;
    for (let k = 0; k < 30; k++) { const m = (lo + hi) / 2; if (place(m).bottom > avail) hi = m; else lo = m; }
    f = lo; L = place(f);
  }
  const off = Math.max(P.box.top, P.box.center - L.bottom / 2);
  const shift = o => o + off;
  L.head.forEach(l => l.base = shift(l.base)); L.sub.forEach(l => l.base = shift(l.base)); L.jp.forEach(l => l.base = shift(l.base));
  L.rule = shift(L.rule); L.short = shift(L.short); L.bottom = shift(L.bottom); L.f = f;

  /* キーワード */
  const kw = String(it.kw || head[0]).toUpperCase();
  const k = ink(kw, font(900, 1000, F_SERIF));
  let ksize = P.kw.w * 1000 / (P.kw.sx * (k.l + k.r)), ksx = P.kw.sx;
  if ((k.a + k.d) * ksize / 1000 > P.kw.maxH) { ksize = P.kw.maxH * 1000 / (k.a + k.d); ksx = P.kw.w * 1000 / (ksize * (k.l + k.r)); }
  L.kw = { t: kw, size: ksize, sx: ksx, x: P.left + k.l * ksize / 1000 * ksx, base: P.kw.cy + (k.a - k.d) / 2 * ksize / 1000 };
  return L;
}

/* 台本 → 描画用の並び */
function prepare(script) {
  const d = new Date((script.date || '') + 'T12:00:00+09:00');
  const ok = !isNaN(d);
  const y = ok ? d.getFullYear() : 2026, mo = ok ? d.getMonth() + 1 : 1, da = ok ? d.getDate() : 1;
  const items = (script.items || []).map((it, i) => ({ ...it, kind: 'news', bg: it.bg || BG_ORDER[i % BG_ORDER.length] }));
  if (script.coffee) items.push({ ...script.coffee, kind: 'coffee', bg: 'E', kw: script.coffee.kw || 'COFFEE BREAK', head: script.coffee.head || ['COFFEE', 'BREAK'] });
  const total = items.length;
  items.forEach((it, i) => {
    const no = pad2(i + 1);
    it.catLeft = it.kind === 'coffee' ? `NOTE ${no}  /  COFFEE BREAK` : `NEWS ${no}  /  ${String(it.cat || '').toUpperCase()}`;
    it.catRight = String(it.topic || '').toUpperCase();
    it.foot = it.kind === 'coffee' ? 'COFFEE BREAK' : `${it.src || ''}${it.date ? '\u2006｜\u2006' + it.date : ''}`;
    it.page = `${no} / ${pad2(total)}`;
    it.credit2 = it.kind === 'coffee' ? (it.bgCredit || CREDIT_COFFEE) : CREDIT_PHOTO;
    it.tags = (it.tags || []).map(s => String(s).toUpperCase());
    it.L = layout(it);
  });
  return {
    items, total, duration: total * DUR,
    header: `${pad2(da)}-${pad2(mo)}-${y} News Shorts｜${y}年${mo}月${da}日 速報ニュース`,
  };
}

/* 横に縮めた文字 */
function textX(ctx, t, x, y, sx, align) {
  ctx.save(); ctx.translate(x, y); ctx.scale(sx, 1); ctx.textAlign = align || 'center'; ctx.fillText(t, 0, 0); ctx.restore();
}
function subLine(ctx, line, size, base) {
  const toks = tokens(line);
  const ws = toks.map(k => adv(k.small ? k.t.toUpperCase() : k.t, font(900, k.small ? size * P.sub.small : size, F_SERIF)) * P.sub.sx);
  let x = P.cx - ws.reduce((a, b) => a + b, 0) / 2;
  toks.forEach((k, i) => {
    if (k.t !== ' ') {
      ctx.font = font(900, k.small ? size * P.sub.small : size, F_SERIF);
      textX(ctx, k.small ? k.t.toUpperCase() : k.t, x, base, P.sub.sx, 'left');
    }
    x += ws[i];
  });
}

function drawBg(ctx, img, t) {
  const s = 1 + P.zoom * (Math.floor(t * FPS + 1e-6) / (DUR * FPS));
  ctx.save();
  ctx.translate(W / 2, H / 2); ctx.scale(s, s); ctx.translate(-W / 2, -H / 2);
  if (img) ctx.drawImage(img, 0, 0, W, H); else { ctx.fillStyle = '#111'; ctx.fillRect(0, 0, W, H); }
  ctx.restore();
}

function drawItem(ctx, show, i, t, bgs) {
  const it = show.items[i], L = it.L;
  ctx.textBaseline = 'alphabetic';
  drawBg(ctx, bgs[it.bg], t);
  ctx.fillStyle = INK;
  /* いつも出ている行 */
  ctx.globalAlpha = 1;
  ctx.font = font(P.header.w, P.header.size, F_SERIF);
  textX(ctx, show.header, P.header.cx, P.header.base, P.header.sx, 'center');
  ctx.font = font(400, P.credit.size, F_SANS);
  ctx.fillStyle = P.credit.color; ctx.textAlign = 'left';
  const mw = ctx.measureText(CREDIT_MUSIC).width, ms = Math.min(P.credit.size, P.credit.size * P.credit.maxW1 / mw);
  ctx.font = font(400, ms, F_SANS);
  ctx.fillText(CREDIT_MUSIC, P.left, P.credit.base1 - (P.credit.size - ms) * 1.33);
  ctx.font = font(400, P.credit.size, F_SANS);
  const cw = ctx.measureText(it.credit2).width, cs = Math.min(P.credit.size, P.credit.size * P.credit.maxW / cw);
  ctx.font = font(400, cs, F_SANS);
  ctx.fillText(it.credit2, P.left, P.credit.base2 - (P.credit.size - cs) * 1.33);
  ctx.fillStyle = INK;

  const a1 = smooth(P.t1, P.t1 + P.fade, t), a2 = smooth(P.t2, P.t2 + P.fade, t), a3 = smooth(P.t3, P.t3 + P.fade, t);
  /* キーワード */
  if (a1 < 1) {
    ctx.globalAlpha = 1 - a1;
    ctx.font = font(900, L.kw.size, F_SERIF);
    textX(ctx, L.kw.t, L.kw.x, L.kw.base, L.kw.sx, 'left');
  }
  if (a1 > 0) {
    ctx.globalAlpha = a1;
    ctx.font = font(P.cat.w, P.cat.size, F_TIMES);
    textX(ctx, it.catLeft, P.left, P.cat.base, P.cat.sx, 'left');
    textX(ctx, it.catRight, P.cat.right, P.cat.base, P.cat.sx, 'right');
    ctx.fillRect(P.left, P.rule1, P.right - P.left, P.rule);
    ctx.font = font(900, L.Sh, F_SERIF);
    L.head.forEach(l => textX(ctx, l.t, P.cx, l.base, P.head.sx, 'center'));
    ctx.fillRect(P.left, L.rule, P.right - P.left, P.rule);
    L.sub.forEach(l => subLine(ctx, l.t, L.Ss, l.base));
    ctx.fillRect(P.cx - P.short.w / 2, L.short, P.short.w, P.rule);
    ctx.fillRect(P.left, P.rule2, P.right - P.left, P.rule);
    ctx.font = font(P.foot.w, P.foot.size, F_SERIF);
    textX(ctx, it.foot, P.left, P.foot.base, P.foot.sx, 'left');
    ctx.font = font(700, P.foot.page, F_TIMES);
    textX(ctx, it.page, P.cat.right, P.foot.base, P.foot.psx, 'right');
  }
  if (a2 > 0) {
    ctx.globalAlpha = a2 * a1;
    ctx.font = font(P.jp.w, P.jp.size, F_SERIF);
    L.jp.forEach(l => textX(ctx, l.t, P.cx, l.base, P.jp.sx, 'center'));
  }
  if (a3 > 0 && it.tags.length) {
    ctx.globalAlpha = a3 * a1;
    ctx.font = font(P.tags.w, P.tags.size, F_TIMES);
    const ws = it.tags.map(s => ctx.measureText(s).width * P.tags.sx);
    let x = P.cx - (ws.reduce((a, b) => a + b, 0) + P.tags.gap * (ws.length - 1)) / 2;
    it.tags.forEach((s, k) => { textX(ctx, s, x, P.tags.base, P.tags.sx, 'left'); x += ws[k] + P.tags.gap; });
  }
  ctx.globalAlpha = 1;
}

function drawFrame(ctx, show, T, bgs) {
  const frame = Math.round(T * FPS);
  const i = Math.min(show.items.length - 1, Math.floor(frame / (DUR * FPS) + 1e-9));
  const t = (frame - i * DUR * FPS) / FPS;
  drawItem(ctx, show, i, t, bgs);
  return i;
}

function fontSpecs() {
  return [font(900, 64, F_SERIF), font(700, 40, F_SERIF), font(P.header.w, 42, F_SERIF), font(P.jp.w, 64, F_SERIF), font(700, 40, F_TIMES), font(400, 20, F_SANS)];
}
function allText(script) {
  const s = [];
  (script.items || []).concat(script.coffee ? [script.coffee] : []).forEach(it => {
    s.push(it.kw, it.cat, it.topic, ...(it.head || []), ...(it.sub || []).map(x => x + x.toUpperCase()), ...(it.jp || []), ...(it.tags || []), it.src, it.date);
  });
  s.push('0123456789 NEWS NOTE COFFEE BREAK News Shorts 年月日速報ニュース ｜ / -', CREDIT_MUSIC, CREDIT_PHOTO, CREDIT_COFFEE);
  return s.filter(Boolean).join(' ');
}

global.NSEngine = { W, H, FPS, DUR, P, BG_ORDER, prepare, drawFrame, drawItem, layout, wrapJp, fontSpecs, allText };
})(window);
