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

  // Handle login form submission
  document.querySelector('.login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('login-password').value;
    
    try {
      const response = await window.api.login(email, password);
      console.log('Login successful:', response);
      
      // Redirect to dashboard
      window.location.href = '/project/dashboard.html';
    } catch (error) {
      alert('Login failed: ' + error.message);
    }
  });

  // Handle signup form submission
  document.querySelector('.signup-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    
    if (password !== confirmPassword) {
      alert('Passwords do not match');
      return;
    }
    
    try {
      const response = await window.api.register({
        email: email,
        username: email, // Use email as username
        password: password,
        password_confirm: confirmPassword,
        first_name: '', // Can be updated later in profile
        last_name: ''
      });
      
      console.log('Registration successful:', response);
      
      // Redirect to dashboard
      window.location.href = '/project/dashboard.html';
    } catch (error) {
      alert('Registration failed: ' + error.message);
    }
  });
});
