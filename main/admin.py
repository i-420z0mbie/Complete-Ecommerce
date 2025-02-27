from django.contrib import admin
from .models import (Category, Product, Store, Order, Cart, Message, Payment,
                     ProductImage, CategoryImage, HeroImage, ProductReview, ProductRating)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['user', 'name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'subcategory', 'sub_subcategory']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if obj is None:
            # For new objects, adjust querysets based on POST data.
            if request.method == 'POST':
                category_id = request.POST.get('category')
                if category_id:
                    form.base_fields['subcategory'].queryset = Category.objects.filter(parent=category_id)
                else:
                    form.base_fields['subcategory'].queryset = Category.objects.none()

                subcategory_id = request.POST.get('subcategory')
                if subcategory_id:
                    form.base_fields['sub_subcategory'].queryset = Category.objects.filter(parent=subcategory_id)
                else:
                    form.base_fields['sub_subcategory'].queryset = Category.objects.none()
            else:
                form.base_fields['subcategory'].queryset = Category.objects.none()
                form.base_fields['sub_subcategory'].queryset = Category.objects.none()
        else:
            # For existing objects, use your custom logic.
            if obj.category:
                current_subcat = obj.subcategory.pk if obj.subcategory else None
                qs = Category.objects.filter(parent=obj.category)
                if current_subcat:
                    qs = qs | Category.objects.filter(pk=current_subcat)
                form.base_fields['subcategory'].queryset = qs
            else:
                form.base_fields['subcategory'].queryset = Category.objects.none()

            if obj.subcategory:
                current_sub_sub = obj.sub_subcategory.pk if obj.sub_subcategory else None
                qs2 = Category.objects.filter(parent=obj.subcategory)
                if current_sub_sub:
                    qs2 = qs2 | Category.objects.filter(pk=current_sub_sub)
                form.base_fields['sub_subcategory'].queryset = qs2
            else:
                form.base_fields['sub_subcategory'].queryset = Category.objects.none()

        return form

    class Media:
        js = ('js/product_admin.js',)



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'store', 'status', 'total_price']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'store', 'status', 'created_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver_user', 'receiver_store', 'is_read', 'content']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'amount', 'payment_method', 'payment_reference', 'is_verified' ]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name',  'parent']

@admin.register(CategoryImage)
class CategoryImageAdmin(admin.ModelAdmin):
    list_display = ['category', 'image']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image']


@admin.register(HeroImage)
class HeroImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'active']

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['author', 'product', 'review']

@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating']