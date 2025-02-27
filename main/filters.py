from django_filters.rest_framework import FilterSet
from .models import Product, Store

class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            "category__slug": ['exact'],
            "subcategory__slug": ['exact'],
            "sub_subcategory__slug": ['exact'],
            "unit_price": ['gt', 'lt']
        }


class StoreFilter(FilterSet):
    class Meta:
        model = Store
        fields = {
            "name": ['exact']
        }