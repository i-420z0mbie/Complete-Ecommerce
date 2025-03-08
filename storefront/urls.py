

from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from main.views import (
    upload_store_logo,
    upload_category_image,
    upload_product_image,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('store/', include('main.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('', include('payment.urls')),
    path("upload/store-logo/", upload_store_logo, name="upload_store_logo"),
    path("upload/category-image/", upload_category_image, name="upload_category_image"),
    path("upload/product-image/", upload_product_image, name="upload_product_image"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)