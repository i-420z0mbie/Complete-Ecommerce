import os
import requests
from django.conf import settings
from .models import Store


def get_default_store():
    """
    Returns the first store in the database.
    You might want to add error handling if no store exists.
    """
    return Store.objects.first()


BUCKETS = {
    "store_logo": "store-logo",
    "category_image": "category-image",
    "hero_image": "hero-image",
    "product_image": "product-image"
}


def upload_to_supabase(file_path, bucket_key):
    bucket_name = BUCKETS.get(bucket_key)
    if not bucket_name:
        print("Invalid bucket key provided. Allowed keys are:", list(BUCKETS.keys()))
        return None

    with open(file_path, "rb") as file:
        file_data = file.read()

    file_name = os.path.basename(file_path)
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
        "Content-Type": "application/octet-stream",
    }

    upload_url = f"{settings.SUPABASE_URL}/storage/v1/object/{bucket_name}/{file_name}"
    response = requests.put(upload_url, headers=headers, data=file_data)

    if response.status_code in (200, 201):
        return f"{settings.MEDIA_URL}{bucket_name}/{file_name}"
    else:
        print("Upload failed:", response.text)
        return None

