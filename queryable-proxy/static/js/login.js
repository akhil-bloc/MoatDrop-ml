document.addEventListener('DOMContentLoaded', function() {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    if (token) {
        window.location.href = '/static/dashboard.html';
    }

    const loginForm = document.getElementById('login-form');
    const alertBox = document.getElementById('alert-box');

    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        // Hide any previous alerts
        alertBox.classList.add('hidden');
        
        try {
            // Create form data for token endpoint
            const formData = new URLSearchParams();
            formData.append('username', email);  // API expects 'username' field
            formData.append('password', password);
            
            const response = await fetch('/auth/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Store token in localStorage
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('user_email', email);
                
                // Redirect to dashboard
                window.location.href = '/static/dashboard.html';
            } else {
                // Show error message
                alertBox.textContent = data.detail || 'Login failed. Please check your credentials.';
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
