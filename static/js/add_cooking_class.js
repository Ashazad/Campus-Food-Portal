document.addEventListener('DOMContentLoaded', function() {
    const addItemForm = document.getElementById('add-item-form');

    addItemForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(addItemForm);

        fetch('/chef/create_cooking_class', {
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
                        window.location.href = '/cooking_classes';
                    }
                });
            } else {
                console.error('Failed to add class. Please try again.');
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
function addRow (arument) {
    var myTable = document.getElementById("class_steps");
    var currentIndex = myTable.rows.length;
    var currentRow = myTable.insertRow(-1);

    var stepsBox = document.createElement("input");
    stepsBox.setAttribute("name", "step_num" + currentIndex);
    stepsBox.setAttribute("type", "number");
    stepsBox.setAttribute("class", "step_num");

    var procBox = document.createElement("textarea");
    procBox.setAttribute("name", "procedure" + currentIndex);
    procBox.setAttribute("type", "textarea");
    procBox.setAttribute("placeholder", "What are we doing at this step?...");

    var imgBox = document.createElement("input");
    imgBox.setAttribute("name", "step_url" + currentIndex);
    imgBox.setAttribute("type", "file");
    imgBox.setAttribute("accept", "image/");

    var removeButton = document.createElement("button");
    removeButton.setAttribute("class", "action-btn");
    removeButton.setAttribute("onclick", "deleteRow(this);");
    removeButton.innerHTML = " - "

    var currentCell = currentRow.insertCell(-1);
    currentCell.appendChild(stepsBox);

    currentCell = currentRow.insertCell(-1);
    currentCell.appendChild(procBox);

    currentCell = currentRow.insertCell(-1);
    currentCell.appendChild(imgBox);

    currentCell = currentRow.insertCell(-1);
    currentCell.appendChild(removeButton);
}
function addRowIngredient () {
    var myTable = document.getElementById("ingredients");
    var currentIndex = myTable.rows.length;
    var currentRow = myTable.insertRow(-1);

    var quantBox = document.createElement("input");
    quantBox.setAttribute("name", "quantity" + currentIndex);
    quantBox.setAttribute("type", "text");
    quantBox.setAttribute("class", "quantity");
    quantBox.setAttribute("placeholder", "e.g. 0.5 cups");

    var nameBox = document.createElement("input");
    nameBox.setAttribute("name", "name" + currentIndex);
    nameBox.setAttribute("type", "text");
    nameBox.setAttribute("placeholder", "e.g. diced apples");


    var removeButton = document.createElement("button");
    removeButton.setAttribute("class", "del-button");
    removeButton.setAttribute("onclick", "deleteRow(this);");
    removeButton.innerHTML = " - "

    var currentCell = currentRow.insertCell(-1);
    currentCell.appendChild(quantBox);

    currentCell = currentRow.insertCell(-1);
    currentCell.appendChild(nameBox);

    currentCell = currentRow.insertCell(-1);
    currentCell.appendChild(removeButton);
}
function deleteRow(o) {

    var p=o.parentNode.parentNode;
        p.parentNode.removeChild(p);
   }