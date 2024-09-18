document.addEventListener('DOMContentLoaded', function () {
    const filterForm = document.getElementById('filter-form');

    filterForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(filterForm);

        let formObject = {};
        formData.forEach((value, key) => {
            formObject[key] = value;
        });

        // Adjust the fetch URL if needed, for example:
        fetch('/chef/marketplace_home_page', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formObject)
        })
        .then(response => response.json())
        .then(data => {
            if(data.is_authenticated === false) {
                // Handle not authenticated state
                Swal.fire({
                    title: 'Please Login',
                    text: 'You need to be logged in to access the Chef Marketplace.',
                    icon: 'warning',
                    confirmButtonText: 'Login'
                }).then((result) => {
                    if (result.isConfirmed) {
                        window.location.href = '/login';
                    }
                });
            } else {
                // Update the food list container with the received HTML
                document.getElementById('food-list-container').innerHTML = data.cooking_class_home;
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
});
