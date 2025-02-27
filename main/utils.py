from .models import Store

def get_default_store():
    """
    Returns the first store in the database.
    You might want to add error handling if no store exists.
    """
    return Store.objects.first()
