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



def upload_to_supabase(file_path, bucket_name="images"):
    """
    Uploads a file to Supabase Storage in the specified bucket.
    Returns the public URL on success, or None if the upload fails.
    """
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
