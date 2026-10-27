(function () {
  // mobile menu
  var burger = document.querySelector('.burger'), menu = document.getElementById('mmenu');
  if (burger && menu) {
    burger.addEventListener('click', function () {
      var open = burger.getAttribute('aria-expanded') === 'true';
      burger.setAttribute('aria-expanded', String(!open));
      menu.hidden = open;
      document.body.classList.toggle('menu-open', !open);
    });
  }
  // accordions
  document.querySelectorAll('.acc-btn').forEach(function (b) {
    b.addEventListener('click', function () {
      var open = b.getAttribute('aria-expanded') === 'true';
      b.setAttribute('aria-expanded', String(!open));
      var p = document.getElementById(b.getAttribute('aria-controls'));
      if (p) p.hidden = open;
    });
  });
  // product gallery carousel (mobile)
  var pg = document.querySelector('.pg');
  if (pg) {
    var slides = pg.querySelectorAll('.pg-slide'), i = 0, ind = pg.querySelector('.pg-ind');
    function go(n) {
      slides[i].classList.remove('on'); i = (n + slides.length) % slides.length; slides[i].classList.add('on');
      if (ind) ind.textContent = (i + 1) + ' / ' + slides.length;
    }
    pg.querySelector('.pg-prev').addEventListener('click', function () { go(i - 1); });
    pg.querySelector('.pg-next').addEventListener('click', function () { go(i + 1); });
    var x0 = null;
    pg.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    pg.addEventListener('touchend', function (e) { if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; if (Math.abs(dx) > 40) go(dx < 0 ? i + 1 : i - 1); x0 = null; });
  }
  // store category filter (breadcrumb links)
  var cats = document.querySelectorAll('.pl-cat');
  if (cats.length) {
    function filter(cat) {
      cats.forEach(function (a) { a.classList.toggle('on', a.dataset.cat === cat); });
      document.querySelectorAll('.pl-item').forEach(function (it) { it.classList.toggle('hide', cat !== 'all' && it.dataset.cat !== cat); });
    }
    cats.forEach(function (a) { a.addEventListener('click', function (e) { e.preventDefault(); history.replaceState(null, '', '#' + a.dataset.cat); filter(a.dataset.cat); }); });
    var h = location.hash.replace('#', '');
    if (h && document.querySelector('.pl-cat[data-cat="' + h + '"]')) filter(h);
  }
})();

/* Forms: submit via fetch to the form relay, keep the visitor on the page, show a thank-you. */
(function () {
  var forms = document.querySelectorAll('form[data-form]');
  forms.forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!f.checkValidity()) { f.reportValidity(); return; }
      var btn = f.querySelector('button[type=submit]');
      var label = btn ? btn.textContent : '';
      if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }
      var data = new FormData(f);
      fetch(f.action, { method: 'POST', body: data, headers: { 'Accept': 'application/json' } })
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(function () {
          var ok = document.createElement('p');
          ok.className = 'fthanks';
          ok.textContent = f.dataset.form === 'newsletter' ? 'Thank you!' : 'Thank you. Your message has been sent.';
          f.replaceWith(ok);
        })
        .catch(function () {
          if (btn) { btn.disabled = false; btn.textContent = label; }
          alert('Sorry — the message could not be sent. Please email info@vandrastudios.com directly.');
        });
    });
  });
})();
