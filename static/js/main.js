document.addEventListener('DOMContentLoaded', function () {
    var createAccountBtn = document.getElementById('create-account-btn');
    if (createAccountBtn) {
        createAccountBtn.addEventListener('click', function () {
            window.location.href = '/create_account'; // Redirect to the Flask route for creating an account
        });
    }

    var loginBtn = document.getElementById('login-btn');
    if (loginBtn) {
        loginBtn.addEventListener('click', function () {
            window.location.href = '/login'; // Redirect to the Flask route for logging in
        });
    }
});
