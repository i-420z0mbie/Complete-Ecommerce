document.addEventListener("DOMContentLoaded", function () {
    const categoryField = document.querySelector("#id_category");
    const subcategoryField = document.querySelector("#id_subcategory");

    if (categoryField && subcategoryField) {
        categoryField.addEventListener("change", function () {
            const categoryId = categoryField.value;

            if (!categoryId) {
                subcategoryField.innerHTML = '<option value="">---------</option>';
                return;
            }

            fetch(`/admin/get-subcategories/?category_id=${categoryId}`)
                .then(response => response.json())
                .then(data => {
                    subcategoryField.innerHTML = '<option value="">---------</option>';
                    data.forEach(sub => {
                        subcategoryField.innerHTML += `<option value="${sub.id}">${sub.name}</option>`;
                    });
                })
                .catch(error => console.error("Error fetching subcategories:", error));
        });
    }
});
