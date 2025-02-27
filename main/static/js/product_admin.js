// your_app/static/js/product_admin.js
document.addEventListener('DOMContentLoaded', function () {
    var categorySelect = document.getElementById('id_category');
    var subcategorySelect = document.getElementById('id_subcategory');
    var subSubcategorySelect = document.getElementById('id_sub_subcategory');

    // Listen for changes on the category field to update subcategories.
    if (categorySelect) {
        categorySelect.addEventListener('change', function () {
            var selectedCategory = this.value;
            if (!selectedCategory) {
                subcategorySelect.innerHTML = '<option value="">---------</option>';
                return;
            }
            // Adjust URL based on your endpoint path.
            fetch('/store/ajax/load-subcategories/?category_id=' + selectedCategory)
                .then(response => response.json())
                .then(data => {
                    subcategorySelect.innerHTML = '<option value="">---------</option>';
                    data.subcategories.forEach(function (subcat) {
                        var option = document.createElement('option');
                        option.value = subcat.id;
                        option.text = subcat.name;
                        subcategorySelect.appendChild(option);
                    });
                })
                .catch(error => console.error('Error loading subcategories:', error));
        });
    }

    // Listen for changes on the subcategory field to update sub‑subcategories.
    if (subcategorySelect) {
        subcategorySelect.addEventListener('change', function () {
            var selectedSubcategory = this.value;
            if (!selectedSubcategory) {
                subSubcategorySelect.innerHTML = '<option value="">---------</option>';
                return;
            }
            fetch('/store/ajax/load-sub-subcategories/?subcategory_id=' + selectedSubcategory)
                .then(response => response.json())
                .then(data => {
                    subSubcategorySelect.innerHTML = '<option value="">---------</option>';
                    data.sub_subcategories.forEach(function (subsubcat) {
                        var option = document.createElement('option');
                        option.value = subsubcat.id;
                        option.text = subsubcat.name;
                        subSubcategorySelect.appendChild(option);
                    });
                })
                .catch(error => console.error('Error loading sub‑subcategories:', error));
        });
    }
});
