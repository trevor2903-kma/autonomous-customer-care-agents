/* Điều khiển trình chiếu dùng chung cho các mẫu slide.
   Phím: → ← (hoặc PageDown/PageUp, Space) chuyển slide; Home/End; F toàn màn hình; G xem lưới; Esc thoát lưới.
   URL: #5 mở slide 5; ?embed ẩn điều khiển (ô xem trước); ?overview mở sẵn chế độ lưới.
   Số trang tự điền vào phần tử có [data-num] (thêm ="pad" để ra 07) và [data-total]. */
(() => {
  const W = 1920;
  const H = 1080;
  const root = document.documentElement;
  const params = new URLSearchParams(location.search);
  const embed = params.has('embed');
  const deck = document.querySelector('.deck');
  const slides = Array.from(deck.children).filter((el) => el.classList.contains('slide'));
  const total = slides.length;
  let current = -1;
  let overview = false;

  if (embed) root.classList.add('deck-embed');

  const fmt = (n, mode) => (mode === 'pad' ? String(n).padStart(2, '0') : String(n));

  slides.forEach((slide, i) => {
    slide.querySelectorAll('[data-num]').forEach((el) => { el.textContent = fmt(i + 1, el.dataset.num); });
    slide.querySelectorAll('[data-total]').forEach((el) => { el.textContent = fmt(total, el.dataset.total); });
    slide.setAttribute('aria-roledescription', 'slide');
    slide.setAttribute('aria-label', `Slide ${i + 1} trên ${total}`);
    slide.setAttribute('aria-hidden', 'true');
    slide.addEventListener('click', () => {
      if (!overview) return;
      go(i);
      setOverview(false);
    });
  });

  // ── Thanh điều khiển ──────────────────────────────────────────
  const icon = (d) => `<svg viewBox="0 0 24 24" aria-hidden="true">${d}</svg>`;
  let ui = null;
  let counter = null;

  if (!embed) {
    ui = document.createElement('nav');
    ui.className = 'deck-ui';
    ui.setAttribute('aria-label', 'Điều khiển trình chiếu');
    ui.innerHTML = [
      `<button type="button" data-act="prev" title="Slide trước (←)" aria-label="Slide trước">${icon('<path d="M15 6l-6 6 6 6"/>')}</button>`,
      '<span class="deck-count" aria-live="polite"></span>',
      `<button type="button" data-act="next" title="Slide sau (→)" aria-label="Slide sau">${icon('<path d="M9 6l6 6-6 6"/>')}</button>`,
      `<button type="button" data-act="grid" title="Xem lưới tất cả slide (G)" aria-label="Xem lưới tất cả slide">${icon('<rect x="4" y="4" width="6.5" height="6.5" rx="1"/><rect x="13.5" y="4" width="6.5" height="6.5" rx="1"/><rect x="4" y="13.5" width="6.5" height="6.5" rx="1"/><rect x="13.5" y="13.5" width="6.5" height="6.5" rx="1"/>')}</button>`,
      `<button type="button" data-act="full" title="Toàn màn hình (F)" aria-label="Toàn màn hình">${icon('<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/>')}</button>`,
    ].join('');
    document.body.appendChild(ui);
    counter = ui.querySelector('.deck-count');
    ui.addEventListener('click', (e) => {
      const btn = e.target.closest('button');
      if (!btn) return;
      const act = btn.dataset.act;
      if (act === 'prev') go(current - 1);
      else if (act === 'next') go(current + 1);
      else if (act === 'grid') setOverview(!overview);
      else if (act === 'full') toggleFullscreen();
    });
  }

  // ── Co giãn và bố cục ─────────────────────────────────────────
  function fit() {
    if (overview) {
      layoutOverview();
      return;
    }
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const s = Math.min(vw / W, vh / H);
    deck.style.transform = `translate(${(vw - W * s) / 2}px, ${(vh - H * s) / 2}px) scale(${s})`;
  }

  function layoutOverview() {
    const pad = 40;
    const gap = 28;
    const vw = root.clientWidth;
    const cols = vw >= 1600 ? 4 : vw >= 1000 ? 3 : 2;
    const cw = (vw - pad * 2 - gap * (cols - 1)) / cols;
    const s = cw / W;
    const ch = H * s;
    deck.style.transform = 'none';
    slides.forEach((slide, i) => {
      const x = pad + (i % cols) * (cw + gap);
      const y = pad + Math.floor(i / cols) * (ch + gap);
      slide.style.transform = `translate(${x}px, ${y}px) scale(${s})`;
    });
    const rows = Math.ceil(total / cols);
    deck.style.height = `${pad * 2 + rows * ch + (rows - 1) * gap}px`;
  }

  function setOverview(on) {
    overview = on;
    root.classList.toggle('deck-overview', on);
    if (!on) {
      slides.forEach((slide) => { slide.style.transform = ''; });
      deck.style.height = '';
      window.scrollTo(0, 0);
    }
    slides.forEach((slide, i) => slide.setAttribute('aria-hidden', on || i === current ? 'false' : 'true'));
    fit();
    if (on) slides[current].scrollIntoView({ block: 'center' });
  }

  // ── Điều hướng ────────────────────────────────────────────────
  function go(i) {
    const next = Math.max(0, Math.min(total - 1, i));
    if (next === current) return;
    if (current >= 0) {
      slides[current].classList.remove('is-active');
      if (!overview) slides[current].setAttribute('aria-hidden', 'true');
    }
    current = next;
    slides[current].classList.add('is-active');
    slides[current].setAttribute('aria-hidden', 'false');
    if (counter) counter.textContent = `${current + 1} / ${total}`;
    if (!embed) {
      const hash = `#${current + 1}`;
      if (location.hash !== hash) {
        try { history.replaceState(null, '', hash); } catch { location.hash = hash; }
      }
    }
    if (overview) slides[current].scrollIntoView({ block: 'nearest' });
  }

  function toggleFullscreen() {
    if (document.fullscreenElement) document.exitFullscreen();
    else if (root.requestFullscreen) root.requestFullscreen().catch(() => {});
  }

  document.addEventListener('keydown', (e) => {
    if (embed || e.altKey || e.ctrlKey || e.metaKey) return;
    const k = e.key;
    const onControl = e.target instanceof Element && e.target.closest('button, a, input, textarea, select');
    if ((k === ' ' || k === 'Enter') && onControl) return;
    if (k === 'ArrowRight' || k === 'ArrowDown' || k === 'PageDown' || k === ' ') {
      e.preventDefault();
      go(current + 1);
    } else if (k === 'ArrowLeft' || k === 'ArrowUp' || k === 'PageUp' || k === 'Backspace') {
      e.preventDefault();
      go(current - 1);
    } else if (k === 'Home') {
      e.preventDefault();
      go(0);
    } else if (k === 'End') {
      e.preventDefault();
      go(total - 1);
    } else if (k === 'Enter') {
      if (overview) setOverview(false);
      else go(current + 1);
    } else if (k === 'f' || k === 'F') {
      toggleFullscreen();
    } else if (k === 'g' || k === 'G' || k === 'o' || k === 'O') {
      setOverview(!overview);
    } else if (k === 'Escape' && overview) {
      setOverview(false);
    }
  });

  // ── Ẩn điều khiển và con trỏ khi đứng yên ─────────────────────
  let idleTimer = 0;
  function wake() {
    ui.classList.add('is-visible');
    root.classList.remove('deck-idle');
    clearTimeout(idleTimer);
    idleTimer = setTimeout(() => {
      ui.classList.remove('is-visible');
      if (!overview) root.classList.add('deck-idle');
    }, 2200);
  }

  if (!embed) {
    window.addEventListener('mousemove', wake);

    let startX = null;
    window.addEventListener('touchstart', (e) => { startX = e.touches[0].clientX; }, { passive: true });
    window.addEventListener('touchend', (e) => {
      if (startX === null || overview) return;
      const dx = e.changedTouches[0].clientX - startX;
      startX = null;
      if (Math.abs(dx) > 50) go(current + (dx < 0 ? 1 : -1));
    });

    window.addEventListener('hashchange', () => {
      const n = parseInt(location.hash.slice(1), 10);
      if (n) go(n - 1);
    });
  }

  window.addEventListener('resize', fit);

  const start = parseInt(location.hash.slice(1), 10);
  go(Number.isFinite(start) ? start - 1 : 0);
  if (!embed && params.has('overview')) setOverview(true);
  else fit();
  if (ui) wake();
})();
