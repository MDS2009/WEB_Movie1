document.addEventListener('DOMContentLoaded', () => {
  const logoutForm = document.getElementById('logout-form');
  const navList = document.querySelector('.navbar-nav.ms-auto');
  if (!logoutForm || !navList) return;

  // LOGOUT_REDIRECT_URL в settings.py указывает на /movies/ (для выхода с обычного сайта),
  // но эта же настройка иначе перехватывает и выход из админки. Явно просим Django admin
  // вернуть после выхода на страницу входа в админку, а не на сайт.
  if (!logoutForm.querySelector('input[name="next"]')) {
    const nextInput = document.createElement('input');
    nextInput.type = 'hidden';
    nextInput.name = 'next';
    nextInput.value = '/admin/login/';
    logoutForm.appendChild(nextInput);
  }

  const li = document.createElement('li');
  li.className = 'nav-item';

  const btn = document.createElement('a');
  btn.href = '#';
  btn.className = 'nav-link';
  btn.title = 'Выйти';
  btn.innerHTML = '<i class="fas fa-sign-out-alt me-1"></i> Выйти';
  btn.addEventListener('click', (e) => {
    e.preventDefault();
    logoutForm.submit();
  });

  li.appendChild(btn);
  navList.insertBefore(li, navList.firstChild);
});
