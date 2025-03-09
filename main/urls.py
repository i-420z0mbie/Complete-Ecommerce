from django.urls import path, include
from rest_framework_nested import routers
from .views import (CategoryViewSet,
                    load_subcategories, load_sub_subcategories,
                    ProductViewSet, ProductImageViewSet, ProductReviewViewSet,
                    ProductRatingViewSet, StoreViewSet, StoreReviewViewSet,
                    StoreRatingViewSet, MessageViewSet, WishListViewSet,
                    CartViewSet, CartItemViewSet, OrderViewSet, StoreOrdersViewSet,
                    HeroImageViewSet, CategoryImageViewSet, PaymentViewSet)
from . import views


router = routers.DefaultRouter()
router.register('categories', viewset=CategoryViewSet, basename='categories')
router.register('products', viewset=ProductViewSet, basename='products')
router.register('stores', viewset=StoreViewSet, basename='stores')
router.register('messages', viewset=MessageViewSet, basename='messages')
router.register('wishlists', viewset=WishListViewSet, basename='wishlists')
router.register('carts', viewset=CartViewSet, basename='carts')
router.register('cart-items', viewset=CartItemViewSet, basename='cart-items')
router.register('orders', viewset=OrderViewSet, basename='orders')
router.register('hero', viewset=HeroImageViewSet, basename='hero-images')
router.register('payments', viewset=PaymentViewSet, basename='payments')



product_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
product_router.register('images', viewset=ProductImageViewSet, basename='product-images')
product_router.register('reviews', viewset=ProductReviewViewSet, basename='product-reviews')
product_router.register('ratings', viewset=ProductRatingViewSet, basename='product-ratings')

store_router = routers.NestedDefaultRouter(router, 'stores', lookup='store')
store_router.register('reviews', viewset=StoreReviewViewSet, basename='store-reviews')
store_router.register('ratings', viewset=StoreRatingViewSet, basename='store-ratings')
store_router.register('orders', viewset=StoreOrdersViewSet, basename='store-orders')

category_router = routers.NestedDefaultRouter(router, 'categories', lookup='category')
category_router.register('images', viewset=CategoryImageViewSet, basename='category-images')


urlpatterns = [

    path('ajax/load-subcategories/', views.load_subcategories, name='ajax_load_subcategories'),
    path('ajax/load-sub-subcategories/', views.load_sub_subcategories, name='ajax_load_sub_subcategories'),
    path('api/send_complaint/', views.send_complaint, name='send_complaint'),
    path('', include(router.urls)),
    path('', include(product_router.urls)),
    path('', include(store_router.urls)),
    path('', include(category_router.urls)),


]
