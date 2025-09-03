document.addEventListener('DOMContentLoaded', () => {
  // password visibility (press and hold to view password)

  document.querySelectorAll('.input-wrapper i').forEach(function(eye) {
    const password = eye.previousElementSibling;

    eye.addEventListener('mousedown', () => {
      password.type = 'text';
    });

    eye.addEventListener('mouseup', () => {
      password.type = 'password';
    });

    eye.addEventListener('mouseleave', () => {
      password.type = 'password';
    });
  });

  // tab switching
  const showTab = (showId, hideId, showTabId, hideTabId) => {
    document.getElementById(showId).style.display = 'block';
    document.getElementById(hideId).style.display = 'none';
    document.getElementById(showTabId).classList.add('active');
    document.getElementById(hideTabId).classList.remove('active');
  };

  document.getElementById('login-tab').addEventListener('click', () => showTab('login-content', 'signup-content', 'login-tab', 'signup-tab'));

  document.getElementById('signup-tab').addEventListener('click', () => showTab('signup-content', 'login-content', 'signup-tab', 'login-tab'));

  document.getElementById('switch-to-signup').addEventListener('click', (e) => {
    e.preventDefault();
    showTab('signup-content', 'login-content', 'signup-tab', 'login-tab');
  });

  document.getElementById('switch-to-login').addEventListener('click', (e) => {
    e.preventDefault();
    showTab('login-content', 'signup-content', 'login-tab', 'signup-tab');
  });
});
