/* NSMusic: the song under the video, repeated without a gap.

   An <audio loop> element stops for a moment each time it goes back to the start (the browser seeks and
   starts decoding again), so the song is played through Web Audio instead: the file is decoded once and
   an AudioBufferSourceNode repeats one stretch of it, sample for sample. Each file holds its 8 bars twice;
   the repeat runs from the end of the first time through to the end of the second (loopStart = one song
   length, loopEnd = two), which is exactly one song length of the same music, so there is no seam.

   iPhone: Web Audio is silent when the ringer switch is off, unless the page is a media player. Setting
   navigator.audioSession.type to "playback" (Safari 17) or playing a silent <audio> alongside (older
   Safari) makes it one. Both happen inside the tap that starts the sound.

     NSMusic.setSong(bytes, loopSeconds)   the song to play (an m4a file); the next play starts it from its top
     NSMusic.play()                        start, or go on from where it was paused; resolves true when it is heard
     NSMusic.pause()                       stop, keeping the place
     NSMusic.on()                          whether it is heard now
     NSMusic.onchange = heard => {}        called when the sound stops or starts by itself (another app took it) */
(function (global) {
  const AC = global.AudioContext || global.webkitAudioContext;
  const IOS = /iP(?:hone|od|ad)/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  const M = { ctx: null, gain: null, src: null, buf: null, bytes: null, loop: 0, paused: true, gen: 0, onchange: null, quiet: null };
  const sleep = ms => new Promise(r => setTimeout(r, ms));

  /* Half a second of silence as a WAV file, for older iPhones (see above). */
  function silence() {
    const n = 4000, b = new ArrayBuffer(44 + n * 2), v = new DataView(b);
    const w = (o, s) => { for (let i = 0; i < s.length; i++) v.setUint8(o + i, s.charCodeAt(i)); };
    w(0, 'RIFF'); v.setUint32(4, 36 + n * 2, true); w(8, 'WAVE'); w(12, 'fmt '); v.setUint32(16, 16, true);
    v.setUint16(20, 1, true); v.setUint16(22, 1, true); v.setUint32(24, 8000, true); v.setUint32(28, 16000, true);
    v.setUint16(32, 2, true); v.setUint16(34, 16, true); w(36, 'data'); v.setUint32(40, n * 2, true);
    return URL.createObjectURL(new Blob([b], { type: 'audio/wav' }));
  }
  function mediaSession() {
    try {
      if (navigator.audioSession) { navigator.audioSession.type = 'playback'; return; }
      if (!IOS) return;
      if (!M.quiet) {
        const q = document.createElement('audio');
        q.src = silence(); q.loop = true; q.setAttribute('playsinline', ''); q.setAttribute('aria-hidden', 'true');
        M.quiet = q;
      }
      const p = M.quiet.play();
      if (p && p.catch) p.catch(() => {});
    } catch (e) {}
  }
  function ctx() {
    if (!M.ctx && AC) {
      M.ctx = new AC();
      M.gain = M.ctx.createGain();
      M.gain.connect(M.ctx.destination);
      M.ctx.onstatechange = () => { if (!M.paused && M.src && M.onchange) M.onchange(on()); };
    }
    return M.ctx;
  }
  function on() { return !!(M.ctx && M.ctx.state === 'running' && M.src && !M.paused); }
  function stopSource() {
    if (!M.src) return;
    try { M.src.stop(); } catch (e) {}
    try { M.src.disconnect(); } catch (e) {}
    M.src = null;
  }
  function setSong(bytes, loopSeconds) {
    M.gen++;
    stopSource();
    M.bytes = bytes || null;
    M.loop = Number(loopSeconds) || 0;
    M.buf = null;
  }
  function decode(c) {
    if (M.buf) return Promise.resolve(M.buf);
    const bytes = M.bytes;
    const copy = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
    return new Promise((ok, ng) => {
      const p = c.decodeAudioData(copy, ok, ng);
      if (p && p.then) p.then(ok, ng);
    }).then(buf => { if (M.bytes === bytes) M.buf = buf; return buf; });
  }
  function startSource(c, buf) {
    const s = c.createBufferSource();
    s.buffer = buf;
    s.loop = true;
    /* One song length of the same music: from the end of the first time through to the end of the last. */
    const reps = M.loop ? Math.floor(buf.duration / M.loop + 1e-3) : 0;
    if (reps >= 2) { s.loopStart = M.loop; s.loopEnd = M.loop * reps; }
    s.connect(M.gain);
    s.start(0, 0);
    M.src = s;
  }
  function play() {
    if (!M.bytes || !AC) return Promise.resolve(false);
    const c = ctx();
    const gen = ++M.gen;
    M.paused = false;
    mediaSession();
    let resumed = Promise.resolve();
    if (c.state !== 'running') { try { resumed = Promise.resolve(c.resume()).catch(() => {}); } catch (e) {} }
    /* Without a tap the browser may keep the sound waiting for ever: give up after a moment. */
    return Promise.race([resumed, sleep(700)]).then(async () => {
      if (gen !== M.gen || c.state !== 'running') return false;
      if (!M.src) {
        const buf = await decode(c);
        if (gen !== M.gen || M.paused) return false;
        if (!M.src) startSource(c, buf);
      }
      return on();
    }).catch(e => { console.warn('music', e); return false; });
  }
  function pause() {
    M.gen++;
    M.paused = true;
    if (M.quiet) { try { M.quiet.pause(); } catch (e) {} }
    if (M.ctx && M.ctx.state === 'running') { try { M.ctx.suspend(); } catch (e) {} }
  }
  /* Back on the page after the phone stopped the sound: try to go on. */
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState !== 'visible' || M.paused || !M.ctx || M.ctx.state === 'running') return;
    try { Promise.resolve(M.ctx.resume()).catch(() => {}); } catch (e) {}
  });
  global.NSMusic = { setSong, play, pause, on, get onchange() { return M.onchange; }, set onchange(f) { M.onchange = f; } };
})(window);
