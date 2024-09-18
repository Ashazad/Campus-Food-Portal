document.addEventListener('DOMContentLoaded', function() {
    const removeFoodItemForm = document.getElementById('remove-food-item');

    removeFoodItemForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const foodID = document.getElementById('Food-Item').value;

        const formData = new FormData();
        formData.append('foodID', foodID);

        fetch('/chef/remove_food_item', {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (response.ok) {
                Swal.fire({
                    icon: 'success',
                    title: 'Successfully removed food item',
                    confirmButtonText: 'Proceed'
                }).then((result) => {
                    if (result.isConfirmed) {
                        window.location.href = '/chef/marketplace_home_page';
                    }
                });
            } else {
                console.error('Failed to remove food item. Please try again.');
                response.json().then(data => {
                    Swal.fire({
                        icon: 'error',
                        title: 'Oops...',
                        text: data.message || 'Something went wrong. Please try again.',
                    });
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Oops...',
                text: 'Something went wrong. Please try again.',
            });
        });
    });
});
