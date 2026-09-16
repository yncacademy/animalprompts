/* ============================================================================
   Video showcase logic — click-to-play with poster frames.
   Videos live only on the GitHub Pages copy of the site (GitHub's 50 MB
   managed-preview cap can't carry them), so every video block is server-
   rendered with data-video attributes and activated lazily:
     * the <video> element is injected only when the user clicks Play
     * on the managed preview (no video assets), the section hides itself
   ========================================================================= */
(function () {
  'use strict';

  var blocks = document.querySelectorAll('[data-video-src]');
  if (!blocks.length) return;

  var origin = location.origin || '';
  var isGithubPages = origin.indexOf('github.io') !== -1 ||
                      origin.indexOf('sifuyik.com') !== -1 ||
                      origin.indexOf('githubusercontent.com') !== -1;
  var hasLocalAssets = !isGithubPages && location.protocol === 'http:' &&
                       origin.indexOf('127.0.0.1') === -1 && origin.indexOf('localhost') === -1;

  function hide(el) {
    el.setAttribute('hidden', '');
  }

  blocks.forEach(function (block) {
    var src = block.getAttribute('data-video-src');
    var poster = block.getAttribute('data-video-poster') || '';

    // Managed preview / file:// — the video assets are not part of that deploy.
    if (!hasLocalAssets && !isGithubPages && (location.protocol === 'file:' ||
        origin.indexOf('autoclaw') !== -1)) {
      hide(block);
      return;
    }

    var btn = block.querySelector('.video-play');
    var stage = block.querySelector('.video-stage');
    if (!btn || !stage) return;

    btn.addEventListener('click', function () {
      if (stage.querySelector('video')) return;
      var v = document.createElement('video');
      v.controls = true;
      v.playsInline = true;
      v.preload = 'metadata';
      v.poster = poster;
      v.setAttribute('playsinline', '');
      v.style.width = '100%';
      v.style.display = 'block';
      v.style.borderRadius = '0';
      var s = document.createElement('source');
      s.src = src;
      s.type = 'video/mp4';
      v.appendChild(s);
      stage.innerHTML = '';
      stage.appendChild(v);
      stage.classList.add('playing');
      var p = v.play();
      if (p && p.catch) { p.catch(function () { /* autoplay policies — user can press play */ }); }
      btn.setAttribute('hidden', '');
    });
  });

  /* ── homepage featured strip: click any card to swap the main player ── */
  var strip = document.querySelector('[data-featured-videos]');
  if (!strip) return;
  var picks = strip.querySelectorAll('.video-thumb');
  var main = document.querySelector('[data-featured-main]');
  if (!picks.length || !main) return;

  picks.forEach(function (t) {
    var link = t.closest('a') || t;
    link.addEventListener('click', function (e) {
      var slug = t.getAttribute('data-slug');
      var src = t.getAttribute('data-video-src');
      var poster = t.getAttribute('data-video-poster') || '';
      var name = t.getAttribute('data-name') || slug;
      e.preventDefault();
      main.innerHTML = '';
      var v = document.createElement('video');
      v.controls = true;
      v.playsInline = true;
      v.autoplay = true;
      v.muted = true;
      v.loop = true;
      v.setAttribute('playsinline', '');
      v.poster = poster;
      var s = document.createElement('source');
      s.src = src;
      s.type = 'video/mp4';
      v.appendChild(s);
      main.appendChild(v);
      var cap = strip.querySelector('.featured-caption');
      if (cap) cap.textContent = name;
      picks.forEach(function (x) { x.classList.toggle('active', x === t); });
      var p = v.play();
      if (p && p.catch) { p.catch(function () {}); }
    });
  });
})();
