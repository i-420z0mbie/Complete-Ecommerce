from django.contrib.auth.models import User

from rest_framework import serializers


from .models import (Category, Product, ProductImage, ProductReview,
                     ProductRating, Store, Message, Cart, CartItem, CategoryImage,
                     StoreReview, StoreRating, WishList, Payment, OrderItem, Order)



class CategoryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryImage
        fields = ['id', 'category', 'image']

    def create(self, validated_data):
        category_id = self.context('category_pk')
        return CategoryImage.objects.create(category_id=category_id, **validated_data)


class CategorySerializer(serializers.ModelSerializer):
    images = CategoryImageSerializer(source='category_images', many=True)
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'images',
            'parent',
            'aliexpress_id',
            'is_active',
            'subcategories'
        ]
        read_only_fields = ['slug']

    def get_subcategories(self, obj):
        subcats = obj.subcategories.filter(is_active=True)
        return CategorySerializer(subcats, many=True).data


from rest_framework import serializers
from .models import HeroImage

class HeroImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroImage
        fields = ['id', 'title', 'description', 'image', 'link', 'active', 'ordering']


class ProductRatingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = ProductRating
        fields = ["user", "username", "rating"]


    def create(self, validated_data):
        product_id = self.context.get('product_pk')
        return ProductRating.objects.create(product_id=product_id, **validated_data)




class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']

    def create(self, validated_data):
        product_id = self.context.get('product_pk')
        return ProductImage.objects.create(product_id=product_id, **validated_data)


class ProductReviewSerializer(serializers.ModelSerializer):
    date_created = serializers.SerializerMethodField()
    author = serializers.CharField(source="author.username", read_only=True)
    class Meta:
        model = ProductReview
        fields = ['id', 'author', 'review', 'date_created']

    def get_date_created(self, obj):
        return obj.date_created.strftime("%A, %d %B %Y")

    def get_author(self, obj):
        return obj.author.username

    def create(self, validated_data):
        product_id = self.context.get('product_pk')
        return ProductReview.objects.create(product_id=product_id, **validated_data)

class SimpleProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    subcategory = serializers.SerializerMethodField()
    sub_subcategory = serializers.SerializerMethodField()
    images = ProductImageSerializer(source='product_images', many=True)

    class Meta:
        model = Product
        fields = ['name', 'category', 'subcategory', 'sub_subcategory', 'images', 'base_price', 'average_rating']

    def get_category(self, obj):
        return obj.category.name if obj.category else None

    def get_subcategory(self, obj):
        return obj.subcategory.name if obj.subcategory else None

    def get_sub_subcategory(self, obj):
        return obj.sub_subcategory.name if obj.sub_subcategory else None

class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)
    quantity = serializers.ReadOnlyField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.product.unit_price * obj.quantity



class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='order_items', many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    amount = serializers.SerializerMethodField()
    shipping_address = serializers.CharField(required=True)
    contact_info = serializers.CharField(required=True)
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user_email', 'items', 'status', 'contact_info',
                  'shipping_address', 'created_at', 'amount']


    def get_created_at(self, obj):
        return obj.created_at.strftime("%A, %d %B %Y")



    def get_amount(self, obj):
        return sum(item.product.unit_price * item.quantity for item in obj.order_items.all())






class StoreReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreReview
        fields = ['user', 'review', 'date_created']

    def create(self, validated_data):
        store_id = self.context.get('store_pk')
        return StoreReview.objects.create(store_id=store_id, **validated_data)





class StoreRatingSerializer(serializers.ModelSerializer):

    user = serializers.ReadOnlyField()

    class Meta:
        model = StoreRating
        fields = ['id', 'user', 'store', 'rating']

    def create(self, validated_data):
        store_id = self.context.get('store_pk')
        return StoreRating.objects.create(store_id=store_id, **validated_data)




class StoreSerializer(serializers.ModelSerializer):

    reviews = StoreReviewSerializer(source='store_reviews', many=True)
    orders = OrderSerializer(many=True, read_only=True)

    class Meta:
        model = Store
        fields = ['id', 'name', 'description', 'logo', 'contact_info', 'reviews', 'orders', 'date_created']

class SimpleStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'logo', 'contact_info', 'description', 'date_created']

class ProductSerializer(serializers.ModelSerializer):
    ratings = ProductRatingSerializer(source='product_ratings', many=True)
    reviews = ProductReviewSerializer(source='product_reviews', many=True, read_only=True)
    store = StoreSerializer(read_only=True)
    category = serializers.SerializerMethodField()
    subcategory = serializers.SerializerMethodField()
    sub_subcategory = serializers.SerializerMethodField()
    images = ProductImageSerializer(source='product_images', many=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'store',
            'name',
            'description',
            'is_dropshipping',
            'aliexpress_id',
            'aliexpress_url',
            'base_price',
            'markup_percentage',
            'store',
            'unit_price',
            'inventory',
            'is_active',
            'date_created',
            'reviews',
            'specification',
            'ratings',
            'category',
            'average_rating',
            'subcategory',
            'sub_subcategory',
            'images'
        ]
        read_only_fields = ['unit_price', 'date_created']

    def get_category(self, obj):
        return obj.category.name if obj.category else None

    def get_subcategory(self, obj):
        return obj.subcategory.name if obj.subcategory else None

    def get_sub_subcategory(self, obj):
        return obj.sub_subcategory.name if obj.sub_subcategory else None


    def get_store(self, obj):
        return obj.store.name





class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)
    receiver_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )
    receiver_store = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver_user', 'receiver_store', 'content', 'is_read', 'timestamp']
        read_only_fields = ['id', 'sender', 'is_read', 'timestamp']



class WishListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishList
        fields = ['id', 'product', 'date_added']



class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'payment_reference', 'status', 'payment_method', 'is_verified', 'date_paid']
        read_only_fields = ['id', 'status', 'is_verified', 'date_paid', 'payment_reference']


class CartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.ReadOnlyField()
    store = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'store', 'status', 'created_at']

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)
    # Use product_id as the write-only field
    product_id = serializers.IntegerField(write_only=True)
    # Include quantity for both reading and writing
    quantity = serializers.IntegerField()
    # Compute total_price on the fly (adjust the calculation if needed)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_id', 'quantity', 'updated_at', 'total_price']

    def get_total_price(self, obj):
        # For example, if Product has a unit_price field:
        return obj.quantity * obj.product.unit_price if obj.product and obj.quantity else 0

















