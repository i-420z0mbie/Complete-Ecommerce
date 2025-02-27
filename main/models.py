import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from django.utils.text import slugify


class Store(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stores')
    name = models.CharField(max_length=150)
    description = models.TextField()
    logo = models.URLField(max_length=500, blank=True, null=True)
    contact_info = models.CharField(max_length=300)
    address = models.CharField(max_length=300)
    date_created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        result = self.store_ratings.aggregate(average=Avg('rating'))
        return result['average'] or 0


class RatingChoices(models.IntegerChoices):
    ONE = 1, '1 star'
    TWO = 2, '2 stars'
    THREE = 3, '3 stars'
    FOUR = 4, '4 stars'
    FIVE = 5, '5 stars'


class StoreRating(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='store_ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RatingChoices.choices, default=RatingChoices.ONE)
    date_created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        unique_together = ('store', 'user')
        ordering = ['-date_created']

    def __str__(self):
        return f'{self.store} - {self.user}: {self.rating}'

class StoreReview(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='store_reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return f'{self.store}-{self.review}'


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    aliexpress_id = models.CharField(max_length=100, unique=True, null=True, blank=True)  # AliExpress category ID
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



class CategoryImage(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_images')
    image = models.URLField(max_length=500, blank=True, null=True)

    objects = models.Manager()


class HeroImage(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.URLField(max_length=500, blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    active = models.BooleanField(default=True)
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordering']

    def __str__(self):
        return self.title or f"HeroImage {self.id}"

    objects = models.Manager()


class Product(models.Model):
    store = models.ForeignKey('Store', on_delete=models.CASCADE, related_name='store_products', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    subcategory = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="sub_products", null=True, blank=True
    )
    sub_subcategory = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="sub_sub_products", null=True, blank=True
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    specification = models.TextField()


    is_dropshipping = models.BooleanField(default=False)
    aliexpress_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    aliexpress_url = models.URLField(max_length=500, null=True, blank=True)

    # Pricing
    base_price = models.DecimalField(max_digits=12, decimal_places=2, null=True,
                                     blank=True)
    markup_percentage = models.FloatField(default=30)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    inventory = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    @property
    def average_rating(self):
        result = self.product_ratings.aggregate(average=Avg('rating'))
        return result['average'] or 0

    def save(self, *args, **kwargs):

        if self.is_dropshipping and self.base_price:
            self.unit_price = self.base_price * (1 + self.markup_percentage / 100)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} - {self.unit_price}'


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.URLField(max_length=500, blank=True, null=True)


    objects = models.Manager()

    def __str__(self):
        return f'{self.image}'
    

class ProductRating(models.Model):

    RATING_ONE = 1
    RATING_TWO = 2
    RATING_THREE= 3
    RATING_FOUR = 4
    RATING_FIVE = 5

    RATING_CHOICES = [
        (RATING_ONE, '1 star'),
        (RATING_TWO, '2 stars'),
        (RATING_THREE, '3 stars'),
        (RATING_FOUR, '4 stars'),
        (RATING_FIVE, '5 stars'),
    ]



    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=RATING_ONE)
    date_created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return f'{self.product}-{self.rating}'


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_reviews')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return f'{self.product}-{self.review}'


class Cart(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.ForeignKey('Store', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    objects = models.Manager()

    def __str__(self):
        return f'{self.user} - {self.status}'

    def calculate_total_price(self):
        # Sum total_price for all related cart items.
        return sum(item.total_price for item in self.cart_items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'product')

    @property
    def total_price(self):
        return self.product.unit_price * self.quantity if self.product else 0

    def save(self, *args, **kwargs):
        if self.quantity <= 0:
            self.delete()
            return
        existing_item = CartItem.objects.filter(cart=self.cart, product=self.product).exclude(id=self.id).first()
        if existing_item:
            existing_item.quantity += self.quantity
            existing_item.save()  # Call save() properly to update the existing item
            return
        super().save(*args, **kwargs)

    objects = models.Manager()

    def __str__(self):
        return f'{self.product} - {self.quantity}'


class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_SHIPPED = "shipped"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='orders')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.ForeignKey('Store', on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    shipping_address = models.CharField(max_length=300)
    contact_info = models.CharField(max_length=10)
    order_reference = models.CharField(max_length=100, unique=True, blank=True, null=True)
    aliexpress_tracking_number = models.CharField(max_length=100, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    @property
    def calculated_total_price(self):
        return sum(item.total_price for item in self.order_items.all())

    def save(self, *args, **kwargs):
        if not self.order_reference:
            self.order_reference = f'ORD-{uuid.uuid4().hex[:8]}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} - {self.total_price}'
    


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)


    @property
    def total_price(self):
        return self.price_at_purchase * self.quantity

    objects = models.Manager()

    def __str__(self):
        return f'{self.order} - {self.quantity}'




    


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver_user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE, related_name='received_messages'
    )
    receiver_store = models.ForeignKey(
        Store, null=True, blank=True, on_delete=models.CASCADE, related_name='store_received_messages'
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def receiver(self):
        # Return whichever receiver is set
        return self.receiver_user if self.receiver_user else self.receiver_store

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.content}"
    # ...


    objects = models.Manager()

    def __str__(self):
        return f'{self.sender}-{self.receiver}-{self.content}'
    

class WishList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return f'{self.user}-{self.product}-{self.date_added}'



class Payment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SUCCESSFUL = 'successful'
    STATUS_FAILED = 'failed'
    STATUS_REFUNDED = 'refunded'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SUCCESSFUL, 'Successful'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_REFUNDED, 'Refunded'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    date_paid = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.payment_reference} - {self.status}"
    
    objects = models.Manager()