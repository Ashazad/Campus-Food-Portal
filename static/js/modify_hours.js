document.addEventListener('DOMContentLoaded', function() {
    const modifyHoursForm = document.getElementById('modify-hours-form');

    modifyHoursForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const startTime = document.getElementById('Starting-Time').value;
        const endTime = document.getElementById('ending-time').value;

        const formData = new FormData();
        formData.append('start_time', startTime);
        formData.append('end_time', endTime);

        fetch('/chef/modify_open_hours', {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (response.ok) {
                Swal.fire({
                    icon: 'success',
                    title: 'Successfully modified open hours',
                    confirmButtonText: 'Proceed'
                }).then((result) => {
                    if (result.isConfirmed) {
                        window.location.href = '/chef/marketplace_home_page';
                    }
                });
            } else {
                console.error('Failed to modify open hours. Please try again.');
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
