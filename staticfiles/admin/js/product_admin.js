document.addEventListener("DOMContentLoaded", function () {
    let categoryField = document.querySelector("#id_category");
    let subcategoryField = document.querySelector("#id_subcategory");

    function updateSubcategories() {
        let categoryId = categoryField.value;
        subcategoryField.innerHTML = '<option value="">---------</option>';

        if (categoryId) {
            fetch(`/admin/get-subcategories/?category_id=${categoryId}`)
                .then(response => response.json())
                .then(data => {
                    data.forEach(subcategory => {
                        let option = new Option(subcategory.name, subcategory.id);
                        subcategoryField.add(option);
                    });
                });
        }
    }

    if (categoryField) {
        categoryField.addEventListener("change", updateSubcategories);
    }
});
