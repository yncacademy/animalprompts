/* ============================================================================
   Character detail page — copy-to-clipboard for prompts + toast feedback.
   Falls back to a selection-based copy when the Clipboard API is unavailable
   (non-secure context), and always reports the outcome to the user.
   ========================================================================= */
(function () {
  'use strict';

  var toastEl = document.getElementById('toast');
  var toastTimer;
  function toast(msg, ok) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.style.background = ok === false ? '#b3261e' : '#1f7a45';
    toastEl.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove('show'); }, 2400);
  }

  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.cssText = 'position:absolute;left:-9999px;top:0';
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
    document.body.removeChild(ta);
    return ok;
  }

  document.querySelectorAll('[data-copy-target]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var src = document.getElementById(btn.dataset.copyTarget);
      if (!src) return;
      var text = src.textContent;

      function done(ok) {
        if (ok) {
          btn.classList.add('copied');
          var label = btn.querySelector('[data-copy-label]');
          var prev = label ? label.textContent : '';
          if (label) label.textContent = 'Copied';
          toast('Prompt copied to clipboard', true);
          setTimeout(function () {
            btn.classList.remove('copied');
            if (label) label.textContent = prev;
          }, 2000);
        } else {
          toast('Copy blocked — select the text and press ⌘C', false);
        }
      }

      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(function () { done(true); },
          function () { done(fallbackCopy(text)); });
      } else {
        done(fallbackCopy(text));
      }
    });
  });
})();
