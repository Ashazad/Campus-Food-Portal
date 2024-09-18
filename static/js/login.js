document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');

    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(loginForm);
        const data = {};
        formData.forEach((value, key) => data[key] = value);
        fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                alert('Login failed. Please check your credentials and try again.');
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
});
