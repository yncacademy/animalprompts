/* ============================================================================
   100 Cute Animal Reference Character Prompts — gallery logic
   Filters: category chips · alphabet index · surprise me
   States: populated · filtered · no-results empty · reset-control visibility.
   (Cards are server-rendered, so there is no loading shell to show.)
   ========================================================================= */
(function () {
  'use strict';

  var DATA = window.CHARACTERS || [];
  var CATS = window.CATEGORIES || [];
  var grid = document.getElementById('grid');
  if (!grid || !DATA.length) return;

  var countEl = document.getElementById('resultCount');
  var emptyEl = document.getElementById('emptyState');
  var emptyMsg = document.getElementById('emptyMsg');
  var catWrap = document.getElementById('catChips');
  var alphaWrap = document.getElementById('alphaIndex');
  var resetBtn = document.getElementById('resetFilters');
  var surpriseBtn = document.getElementById('surpriseBtn');

  var state = { cat: 'all', letter: 'all' };

  /* ── category colour lookup, applied inline as a data-driven token ───── */
  var CAT_COLOR = {
    'pets-farm': 'var(--cat-pets-farm)',
    'forest-meadow': 'var(--cat-forest-meadow)',
    'jungle-savanna': 'var(--cat-jungle-savanna)',
    'ocean-reef': 'var(--cat-ocean-reef)',
    'birds-sky': 'var(--cat-birds-sky)',
    'reptiles-amphibians': 'var(--cat-reptiles-amphibians)',
    'tiny-critters': 'var(--cat-tiny-critters)'
  };
  function catColor(id) { return CAT_COLOR[id] || 'var(--muted)'; }

  /* ── URL sync so a filtered view is shareable + back-button friendly ─── */
  function readUrl() {
    var q = new URLSearchParams(location.search);
    var c = q.get('category');
    var l = q.get('letter');
    if (c && CATS.some(function (x) { return x.id === c; })) state.cat = c;
    if (l && /^[a-z]$/i.test(l)) state.letter = l.toUpperCase();
  }
  function writeUrl() {
    var q = new URLSearchParams();
    if (state.cat !== 'all') q.set('category', state.cat);
    if (state.letter !== 'all') q.set('letter', state.letter);
    var s = q.toString();
    history.replaceState(null, '', s ? '?' + s : location.pathname);
  }

  /* ── filters ─────────────────────────────────────────────────────────── */
  function matches(c) {
    if (state.cat !== 'all' && c.cat !== state.cat) return false;
    if (state.letter !== 'all' && c.name.charAt(0).toUpperCase() !== state.letter) return false;
    return true;
  }

  /* ── card markup ─────────────────────────────────────────────────────── */
  function cardHTML(c) {
    var num = (c.n < 10 ? '0' : '') + c.n;
    return '' +
      '<a class="card" href="character/' + c.slug + '.html" style="--cat-color:' + catColor(c.cat) + '">' +
        '<div class="card-media">' +
          '<img src="' + c.thumb + '" width="560" height="700" loading="lazy" decoding="async" ' +
               'alt="' + esc(c.name) + ' — ' + esc(c.species) + ' character reference sheet">' +
          '<span class="card-no" aria-hidden="true">' + num + '</span>' +
        '</div>' +
        '<div class="card-body">' +
          '<h3 class="card-name">' + esc(c.name) + '</h3>' +
          '<p class="card-species">' + esc(c.species) + '</p>' +
          '<span class="card-cat"><span class="dot" aria-hidden="true"></span>' + esc(c.catLabel) + '</span>' +
        '</div>' +
      '</a>';
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (m) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m];
    });
  }

  /* ── render ──────────────────────────────────────────────────────────── */
  var renderToken = 0;
  function render() {
    var list = DATA.filter(matches);
    var token = ++renderToken;

    grid.innerHTML = list.map(cardHTML).join('');

    var n = list.length;
    if (countEl) {
      countEl.innerHTML = '<b>' + n + '</b> ' + (n === 1 ? 'character' : 'characters') +
        (state.cat !== 'all' || state.letter !== 'all' ? ' shown' : ' in the collection');
    }
    if (emptyEl) emptyEl.hidden = n !== 0;
    if (emptyMsg) {
      var bits = [];
      if (state.letter !== 'all') bits.push('starting with “' + state.letter + '”');
      if (state.cat !== 'all') {
        var cat = CATS.filter(function (x) { return x.id === state.cat; })[0];
        if (cat) bits.push('in ' + cat.label);
      }
      emptyMsg.textContent = bits.length
        ? 'Nothing matches ' + bits.join(' ') + '. Try clearing a filter.'
        : 'Try a different combination of filters.';
    }
    if (resetBtn) resetBtn.hidden = (state.cat === 'all' && state.letter === 'all');
    if (token !== renderToken) return;
  }

  /* ── build filter chrome ─────────────────────────────────────────────── */
  function buildCats() {
    var total = DATA.length;
    var html = chip('all', 'All characters', total, 'var(--accent)');
    CATS.forEach(function (cat) {
      html += chip(cat.id, cat.label, cat.count, catColor(cat.id));
    });
    catWrap.innerHTML = html;
    catWrap.addEventListener('click', function (e) {
      var b = e.target.closest('button[data-cat]');
      if (!b) return;
      state.cat = b.dataset.cat;
      syncCats(); writeUrl(); render();
    });
  }
  function chip(id, label, count, color) {
    return '<button type="button" class="chip" data-cat="' + id + '" aria-pressed="' +
      (state.cat === id) + '" style="--cat-color:' + color + '">' +
      '<span class="dot" aria-hidden="true"></span>' + esc(label) +
      '<span class="count">' + count + '</span></button>';
  }
  function syncCats() {
    catWrap.querySelectorAll('button[data-cat]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.cat === state.cat));
    });
  }

  function buildAlpha() {
    var used = {};
    DATA.forEach(function (c) { used[c.name.charAt(0).toUpperCase()] = true; });
    var html = '<button type="button" data-letter="all" aria-pressed="' + (state.letter === 'all') + '">All</button>';
    for (var i = 65; i <= 90; i++) {
      var L = String.fromCharCode(i);
      var has = !!used[L];
      html += '<button type="button" data-letter="' + L + '" aria-pressed="' + (state.letter === L) + '"' +
        (has ? '' : ' disabled aria-disabled="true"') + '>' + L + '</button>';
    }
    alphaWrap.innerHTML = html;
    alphaWrap.addEventListener('click', function (e) {
      var b = e.target.closest('button[data-letter]');
      if (!b || b.disabled) return;
      state.letter = b.dataset.letter;
      syncAlpha(); writeUrl(); render();
    });
  }
  function syncAlpha() {
    alphaWrap.querySelectorAll('button[data-letter]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.letter === state.letter));
    });
  }

  /* ── actions ─────────────────────────────────────────────────────────── */
  if (resetBtn) {
    resetBtn.addEventListener('click', function () {
      state.cat = 'all'; state.letter = 'all';
      syncCats(); syncAlpha(); writeUrl(); render();
      toast('Filters cleared');
    });
  }
  if (surpriseBtn) {
    surpriseBtn.addEventListener('click', function () {
      var pool = DATA.filter(matches);
      if (!pool.length) pool = DATA;
      var pick = pool[Math.floor(Math.random() * pool.length)];
      location.href = 'character/' + pick.slug + '.html';
    });
  }

  /* ── toast ───────────────────────────────────────────────────────────── */
  var toastEl = document.getElementById('toast');
  var toastTimer;
  function toast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove('show'); }, 2200);
  }

  /* ── init ────────────────────────────────────────────────────────────── */
  readUrl();
  buildCats();
  buildAlpha();
  render();
  window.addEventListener('popstate', function () { readUrl(); syncCats(); syncAlpha(); render(); });
})();
