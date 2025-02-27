// your_app/static/js/product_admin.js
document.addEventListener('DOMContentLoaded', function () {
    var categorySelect = document.getElementById('id_category');
    var subcategorySelect = document.getElementById('id_subcategory');

    if (categorySelect) {
        categorySelect.addEventListener('change', function () {
            var selectedCategory = this.value;
            // If no category is selected, clear subcategory options.
            if (!selectedCategory) {
                subcategorySelect.innerHTML = '<option value="">---------</option>';
                return;
            }
            // Make an AJAX call to fetch subcategories for the selected category.
            fetch('/admin/ajax/load-subcategories/?category_id=' + selectedCategory)
                .then(response => response.json())
                .then(data => {
                    // Clear current options
                    subcategorySelect.innerHTML = '<option value="">---------</option>';
                    // Populate new options with the returned subcategories.
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
});
