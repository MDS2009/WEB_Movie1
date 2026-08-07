console.log('RV КИНО JS загружен');

document.addEventListener('DOMContentLoaded', () => {
  // ===== Cookie modal =====
  const cookieModal = document.getElementById('cookie-modal');
  if (cookieModal) {
    const acceptBtn = document.getElementById('cookie-accept-btn');
    const declineBtn = document.getElementById('cookie-decline-btn');

    const hideCookie = () => (cookieModal.style.display = 'none');
    const setConsentCookie = (value) => {
      document.cookie = `cookie_consent=${value}; max-age=2592000; path=/`;
    };

    acceptBtn?.addEventListener('click', () => { setConsentCookie('true'); hideCookie(); });
    declineBtn?.addEventListener('click', () => { setConsentCookie('false'); hideCookie(); });
  }

  // ===== "Not available" modal =====
  const watchBtn = document.getElementById('watch-btn');
  const notAvailModal = document.getElementById('not-available-modal');
  const notAvailClose = document.getElementById('modal-close-btn');

  if (watchBtn && notAvailModal && notAvailClose) {
    watchBtn.addEventListener('click', () => notAvailModal.classList.add('active'));
    notAvailClose.addEventListener('click', () => notAvailModal.classList.remove('active'));
    notAvailModal.addEventListener('click', (e) => {
      if (e.target === notAvailModal) notAvailModal.classList.remove('active');
    });
  }

  // ===== Burger menu =====
  const burger = document.getElementById('burger-btn');
  const navMenu = document.getElementById('nav-menu');
  const hero = document.querySelector('.hero'); // вместо getElementById('.hero')
  if (burger && navMenu) {
    burger.addEventListener('click', () => {
      navMenu.classList.toggle('active');
      hero?.classList.toggle('menu-open');
    });
  }

  // ===== Policy consent =====
  const policyBox = document.getElementById('policy-consent-box');
  const policyAcceptBtn = document.getElementById('policy-accept-btn');
  if (policyBox && policyAcceptBtn) {
    const hasConsent = document.cookie.split('; ').find(row => row.startsWith('policy_consent='));
    if (hasConsent && hasConsent.split('=')[1] === 'true') {
      policyBox.style.display = 'none';
    }
    policyAcceptBtn.addEventListener('click', () => {
      document.cookie = 'policy_consent=true; max-age=31536000; path=/';
      policyBox.style.display = 'none';
    });
  }

  // ===== Player modal (Смотреть/Трейлер) =====
  const playerModal = document.getElementById('player-modal');
  const playerCloseBtn = document.getElementById('player-close-btn');
  const playerIframe = document.getElementById('player-iframe');
  const playerTitle = document.getElementById('player-title');
  const playerMessage = document.getElementById('player-message');

  const showMessage = (caption) => {
      if (playerTitle) playerTitle.textContent = caption || 'Плеер';
      if (playerIframe) playerIframe.style.display = 'none';
      if (playerMessage) playerMessage.style.display = 'flex';
      if (playerIframe) playerIframe.src = '';
      playerModal?.classList.add('active');
  };

  const showIframe = (src, caption) => {
      if (playerTitle) playerTitle.textContent = caption || 'Плеер';
      if (playerMessage) playerMessage.style.display = 'none';
      if (playerIframe) playerIframe.style.display = 'block';
      if (playerIframe) playerIframe.src = src;
      playerModal?.classList.add('active');
  };

  const isVkEmbed = (url) => {
      try {
        const u = new URL(url);
        return u.hostname.includes('vkvideo.ru') && u.pathname.includes('video_ext.php');
      } catch {
        return false;
      }
  };

    const openPlayer = (src, caption) => {
      if (!playerModal || !playerIframe) return;

      if (!src) {
        showMessage(caption);
        return;
      }

      // если дали не embed-ссылку, тоже показываем сообщение (или можно подсказку)
      if (!isVkEmbed(src)) {
        showMessage(caption);
        return;
      }

      showIframe(src, caption);
  };

   const closePlayer = () => {
      if (!playerModal || !playerIframe) return;
      playerModal.classList.remove('active');
      playerIframe.src = '';
      if (playerMessage) playerMessage.style.display = 'none';
      playerIframe.style.display = 'block';
   };


  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.js-open-player');
    if (btn) openPlayer(btn.dataset.src, btn.dataset.title);

    if (playerModal && e.target === playerModal) closePlayer();
  });

  playerCloseBtn?.addEventListener('click', closePlayer);

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closePlayer();
  });

  // ===== Tabs (страница фильма/сериала/шоу: Описание/Актёры/Отзывы) =====
  document.querySelectorAll('.tabs-nav').forEach((nav) => {
    const links = nav.querySelectorAll('.tab-link');
    const panelsContainer = nav.parentElement;
    links.forEach((link) => {
      link.addEventListener('click', () => {
        const target = link.dataset.tab;
        links.forEach((l) => l.classList.toggle('active', l === link));
        panelsContainer.querySelectorAll(':scope > .tab-panel').forEach((panel) => {
          panel.classList.toggle('active', panel.dataset.tabPanel === target);
        });
      });
    });
  });

  // ===== Sticky CTA bar (появляется, когда основная кнопка "Смотреть" уходит со скролла) =====
  const ctaRow = document.getElementById('cta-row');
  const stickyBar = document.getElementById('sticky-cta-bar');
  if (ctaRow && stickyBar && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(
      ([entry]) => stickyBar.classList.toggle('visible', !entry.isIntersecting),
      { threshold: 0 }
    );
    observer.observe(ctaRow);
  }

  // ===== Management dropdown (сообщества) =====
  document.addEventListener('click', (e) => {
    const toggle = e.target.closest('.manage-dropdown-toggle');
    if (toggle) {
      const menu = toggle.parentElement.querySelector('.manage-dropdown-menu');
      const wasOpen = menu?.classList.contains('open');
      document.querySelectorAll('.manage-dropdown-menu.open').forEach((m) => m.classList.remove('open'));
      if (menu && !wasOpen) menu.classList.add('open');
      return;
    }
    if (!e.target.closest('.manage-dropdown-menu')) {
      document.querySelectorAll('.manage-dropdown-menu.open').forEach((m) => m.classList.remove('open'));
    }
  });

});

document.addEventListener('click', (e) => {
  const btn = e.target.closest('[data-scroll]');
  if (!btn) return;

  const el = document.getElementById(btn.dataset.scroll);
  if (!el) return;

  const dir = parseInt(btn.dataset.dir || '1', 10);

  const firstItem = el.querySelector('.rail-card, .hero-slide');
  if (!firstItem) return;

  const gap = parseFloat(getComputedStyle(el).columnGap || getComputedStyle(el).gap || '0') || 0;
  const step = firstItem.getBoundingClientRect().width + gap;

  el.scrollBy({ left: dir * step, behavior: 'smooth' });
});

window.rvAdmin = (cmd = '') => {
  if (String(cmd).trim().toLowerCase() === 'admin') {
    window.location.href = '/admin/';
    return true;
  }
  return false;
};

