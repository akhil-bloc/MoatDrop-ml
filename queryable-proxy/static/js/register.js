document.addEventListener('DOMContentLoaded', function() {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    if (token) {
        window.location.href = '/static/dashboard.html';
    }

    const registerForm = document.getElementById('register-form');
    const alertBox = document.getElementById('alert-box');

    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        
        // Hide any previous alerts
        alertBox.classList.add('hidden');
        
        // Check if passwords match
        if (password !== confirmPassword) {
            alertBox.textContent = 'Passwords do not match.';
            alertBox.classList.remove('hidden');
            alertBox.classList.add('alert-danger');
            return;
        }
        
        try {
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Show success message
                alertBox.textContent = 'Registration successful! Redirecting to login...';
                alertBox.classList.remove('hidden');
                alertBox.classList.remove('alert-danger');
                alertBox.classList.add('alert-success');
                
                // Redirect to login page after a short delay
                setTimeout(() => {
                    window.location.href = '/static/login.html';
                }, 2000);
            } else {
                // Show error message
                alertBox.textContent = data.detail || 'Registration failed. Please try again.';
                alertBox.classList.remove('hidden');
                alertBox.classList.add('alert-danger');
            }
        } catch (error) {
            console.error('Error:', error);
            alertBox.textContent = 'An error occurred. Please try again later.';
            alertBox.classList.remove('hidden');
            alertBox.classList.add('alert-danger');
        }
    });
});
