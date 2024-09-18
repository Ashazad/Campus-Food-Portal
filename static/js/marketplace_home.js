document.addEventListener('DOMContentLoaded', function () {
    const orderButtons = document.querySelectorAll('.order-btn');
    orderButtons.forEach(button => {
        button.addEventListener('click', function () {
            document.getElementById('popup-wrapper').style.display = 'block';
        });
    });

    // Add event listener to close the popup
    document.getElementById('close-popup').addEventListener('click', function () {
        document.getElementById('popup-wrapper').style.display = 'none';
    });

    // Add event listener for order form submission
    document.getElementById('order-form').addEventListener('submit', function (e) {
        e.preventDefault();
        // Collect credit card information
        const cardNumber = document.getElementById('card-number').value;
        const expiryDate = document.getElementById('expiry-date').value;
        const cvv = document.getElementById('cvv').value;
        // Send to processing
        fetch('/process_order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ cardNumber, expiryDate, cvv }),
        })
        .then(response => {
            // Handle the response from the server
            document.getElementById('popup-wrapper').style.display = 'none';
            alert('Order placed successfully!');
        })
        .catch(error => {
            // Handle errors
            console.error('Error:', error);
            alert('An error occurred while placing the order.');
        });
    });

    // Filter form submission event listener
    const filterForm = document.getElementById('filter-form');
    const classId = document.getElementById('card-link');
    var href = "cooking_classes/view/" + classId;
    filterForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(filterForm);

        let formObject = {};
        formData.forEach((value, key) => {
            formObject[key] = value;
        });

        // Adjust the fetch URL if needed, for example:
        fetch('/marketplace_home_page', {
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
                document.getElementById('food-list-container').innerHTML = data.foods_html;
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
});