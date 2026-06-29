// JL Fitness — main.js

// Opening text sequence intro overlay
(function () {
  var overlay = document.getElementById('introOverlay');
  if (!overlay) return;

  // Show once per session; skip on return visits
  if (sessionStorage.getItem('introSeen')) {
    overlay.classList.add('intro-hidden');
    return;
  }

  document.body.style.overflow = 'hidden';

  // At 2.5s begin fade-out; at completion hide the overlay and unlock scroll
  setTimeout(function () {
    overlay.classList.add('intro-out');
    overlay.addEventListener('animationend', function () {
      overlay.classList.add('intro-hidden');
      document.body.style.overflow = '';
      sessionStorage.setItem('introSeen', '1');
    }, { once: true });
  }, 2500);
})();

// Mobile nav toggle
(function () {
  const toggle = document.querySelector('.nav-toggle');
  const nav    = document.querySelector('#site-nav');
  if (!toggle || !nav) return;
  toggle.addEventListener('click', function () {
    const open = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open);
  });
  // Close on outside click
  document.addEventListener('click', function (e) {
    if (!toggle.contains(e.target) && !nav.contains(e.target)) {
      nav.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });
})();

// Reveal on scroll
(function () {
  if (!document.documentElement.classList.contains('js')) return;
  const els = document.querySelectorAll('.reveal');
  if (!els.length) return;
  const io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('in');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  els.forEach(function (el) { io.observe(el); });
})();

// Filter buttons (shop page)
(function () {
  const btns = document.querySelectorAll('.filter-btn');
  if (!btns.length) return;
  btns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      btns.forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      const filter = btn.dataset.filter;
      document.querySelectorAll('.product-card').forEach(function (card) {
        if (filter === 'all' || card.dataset.category === filter) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });
})();

// Simple contact form intercept (prevent default, show success)
(function () {
  const form = document.querySelector('.contact-form');
  if (!form) return;
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    if (btn) { btn.textContent = 'Message Sent ✓'; btn.disabled = true; btn.style.background = '#1a3a00'; }
  });
})();
