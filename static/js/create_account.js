document.addEventListener('DOMContentLoaded', function() {
    const accountTypeSelect = document.getElementById('account-type');
    const chefOnlyFields = document.querySelectorAll('.chef-only');
    const businessNameInput = document.getElementById('business-name');
    const locationInput = document.getElementById('location');
    const mapImage = document.getElementById('map-image'); // Get map image
    const buildingLocationSelect = document.getElementById('map-options');
    const pinImage = document.getElementById('pin-image'); // Get pin image

    // Function to toggle the display of chef-only fields
    function toggleChefFields() {
        const isChef = accountTypeSelect.value === 'chef';
        chefOnlyFields.forEach(field => {
            field.style.display = isChef ? 'block' : 'none';
        });
        businessNameInput.required = isChef;
        locationInput.required = isChef;
        if (isChef) {
            pinLocation(); // Update pin location based on the current selection
        }
    }
    function pinLocation() {
        const selectedLocation = buildingLocationSelect.value;
        let positions = {
            'DeerField': { top: '41%', left: '10%' },
            'CCIT': { top: '25%', left: '35%' },
            'Instruction Centre': { top: '15%', left: '20%' },
            'Kaneff Centre': { top: '42%', left: '46%' },
            'MN': { top: '38%', left: '7%' },
            'Davis': { top: '37%', left: '53%' },
            'HealthSci Complex': { top: '17%', left: '43%' },
        };

        if (positions[selectedLocation]) {
            pinImage.style.top = positions[selectedLocation].top;
            pinImage.style.left = positions[selectedLocation].left;
            pinImage.style.display = 'block'; // Show the pin
        } else {
            pinImage.style.display = 'none'; // Hide the pin if no location is selected
        }
    }


    // Initial toggle based on the preselected value
    toggleChefFields();
    pinLocation();
    // Event listener for when the account type changes
    accountTypeSelect.addEventListener('change', toggleChefFields);
    buildingLocationSelect.addEventListener('change', pinLocation);

    const createAccountForm = document.getElementById('create-account-form');
    createAccountForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(createAccountForm);
        const jsonFormData = Object.fromEntries(formData.entries());
        if(accountTypeSelect.value !== 'chef') {
            delete jsonFormData['business-name'];
            delete jsonFormData['location'];
        }
        fetch('/create_account', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(jsonFormData),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Account Created',
                    text: data.message,
                }).then(() => {
                    window.location.href = '/login';
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Oops...',
                    text: data.message,
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
