/* ============================================================
   Harry's Site — script.js
   Minimal JavaScript — no libraries, no frameworks
   ============================================================ */

/* ── HIT COUNTER ──
   Slowly ticks up every 8 seconds, like a real CGI counter.
   Uses ('000000' + n).slice(-6) instead of padStart() for
   compatibility with Safari 4 and 5. */
(function () {
  var counter = document.getElementById('counter');
  if (!counter) return;

  var count = 12847;

  function pad6(n) {
    return ('000000' + n).slice(-6);
  }

  function tick() {
    count += Math.floor(Math.random() * 2);
    counter.innerHTML = pad6(count);
  }

  setInterval(tick, 8000);
}());
