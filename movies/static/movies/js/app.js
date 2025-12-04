// Простой JS — для будущих эффектов и тестов
console.log('RV КИНО JS загружен');

// Плавная прокрутка (пример)
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    if (this.getAttribute('href') !== '#') return;
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});

document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("cookie-modal");
    if (!modal) return;

    const acceptBtn = document.getElementById("cookie-accept-btn");
    const declineBtn = document.getElementById("cookie-decline-btn");

    const hideModal = () => {
        modal.style.display = "none";
    };

    const setConsentCookie = (value) => {
        // кука на 30 дней
        document.cookie = `cookie_consent=${value}; max-age=2592000; path=/`;
    };

    acceptBtn?.addEventListener("click", () => {
        setConsentCookie("true");
        hideModal();
    });

    declineBtn?.addEventListener("click", () => {
        setConsentCookie("false");
        hideModal();
    });
});

// Модалка "фильм недоступен"
document.addEventListener('DOMContentLoaded', () => {
  const watchBtn = document.getElementById('watch-btn');
  const modal = document.getElementById('not-available-modal');
  const closeBtn = document.getElementById('modal-close-btn');

  if (watchBtn && modal && closeBtn) {
    watchBtn.addEventListener('click', () => {
      modal.classList.add('active');
    });

    closeBtn.addEventListener('click', () => {
      modal.classList.remove('active');
    });

    // закрытие по клику по фону
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.remove('active');
      }
    });
  }
});

document.addEventListener('DOMContentLoaded', () => {
  const burger = document.getElementById('burger-btn');
  const navMenu = document.getElementById('nav-menu');
  const hero = document.getElementById('.hero')

  if (burger && navMenu) {
    burger.addEventListener('click', () => {
      navMenu.classList.toggle('active');
      hero?.classList.toggle('menu-open')
    });
  }
});

document.addEventListener('DOMContentLoaded', () => {
  const policyBox = document.getElementById('policy-consent-box');
  const policyAcceptBtn = document.getElementById('policy-accept-btn');

  if (policyBox && policyAcceptBtn) {
    // читаем cookie policy_consent
    const hasConsent = document.cookie
      .split('; ')
      .find(row => row.startsWith('policy_consent='));

    if (hasConsent && hasConsent.split('=')[1] === 'true') {
      // уже принято — прячем блок
      policyBox.style.display = 'none';
    }

    policyAcceptBtn.addEventListener('click', () => {
      // ставим куку на 1 год
      document.cookie = 'policy_consent=true; max-age=31536000; path=/';
      policyBox.style.display = 'none';
    });
  }
});
