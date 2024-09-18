document.addEventListener('DOMContentLoaded', function() {
    const addItemForm = document.getElementById('add-item-form');

    addItemForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(addItemForm);

        fetch('/chef/add_food_item', {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (response.ok) {
                Swal.fire({
                    icon: 'success',
                    title: 'Successfully added item',
                    confirmButtonText: 'Proceed'
                }).then((result) => {
                    if (result.isConfirmed) {
                        window.location.href = '/chef/marketplace_home_page';
                    }
                });
            } else {
                console.error('Failed to add food item. Please try again.');
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
