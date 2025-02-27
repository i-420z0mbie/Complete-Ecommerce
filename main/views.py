import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import upload_to_supabase
from django.db.models import Q
from django.http import JsonResponse
from .utils import get_default_store
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from .filters import ProductFilter, StoreFilter
from .models import (Category, Product, ProductImage, ProductReview, ProductRating, Message, WishList, Payment,
                     Store, StoreReview, StoreRating, Cart, CartItem, Order, OrderItem, HeroImage, CategoryImage)
from .serializers import (CategorySerializer, ProductSerializer,
                          ProductImageSerializer, ProductReviewSerializer,
                          ProductRatingSerializer, StoreSerializer,
                          StoreReviewSerializer, StoreRatingSerializer,
                          MessageSerializer, WishListSerializer,
                          PaymentSerializer, CartSerializer, CartItemSerializer,
                          OrderSerializer, OrderItemSerializer, HeroImageSerializer, CategoryImageSerializer)






def load_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = Category.objects.filter(
        parent_id=category_id,
        is_active=True
    ).values('id', 'name', 'slug')  # Add slug if needed for URLs

    return JsonResponse({
        'subcategories': list(subcategories)
    })


def load_sub_subcategories(request):
    subcategory_id = request.GET.get('subcategory_id')
    sub_subcategories = Category.objects.filter(
        parent_id=subcategory_id,
        is_active=True
    ).values('id', 'name', 'slug')  # Add slug if needed

    return JsonResponse({
        'sub_subcategories': list(sub_subcategories)
    })

class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.filter(parent__isnull=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class HeroImageViewSet(ReadOnlyModelViewSet):
    queryset = HeroImage.objects.filter(active=True).order_by('ordering')
    serializer_class = HeroImageSerializer
    permission_classes = [AllowAny]




class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True).prefetch_related('product_images').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'category__name', 'subcategory__name', 'sub_subcategory__name']
    ordering_fields = ['unit_price', 'date_created']
    permission_classes = [AllowAny]


class ProductImageViewSet(ReadOnlyModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [AllowAny]


    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_pk': self.kwargs['product_pk']}


class ProductReviewViewSet(ModelViewSet):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return ProductReview.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_pk': self.kwargs['product_pk']}

    def perform_create(self, serializer):
        user = self.request.user

        serializer.save(author=user)

    def perform_update(self, serializer):
        user = self.request.user

        if serializer.instance.author != user:
            raise PermissionDenied("You are not allowed to edit this post!")
        serializer.save()


    def perform_destroy(self, instance):
        user = self.request.user

        if instance.author != user:
            raise PermissionDenied("You are not allowed to perform this task")
        instance.delete()


class ProductRatingViewSet(ModelViewSet):
    queryset = ProductRating.objects.all()
    serializer_class = ProductRatingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return ProductRating.objects.filter(product_id=self.kwargs['product_pk'])


    def get_serializer_context(self):
        return {'product_pk': self.kwargs['product_pk']}

    def perform_create(self, serializer):
        user = self.request.user

        serializer.save()



class StoreViewSet(ReadOnlyModelViewSet):
    queryset = Store.objects.prefetch_related('store_reviews').all()
    serializer_class = StoreSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name']
    filterset_class = StoreFilter
    permission_classes = [AllowAny]


class StoreReviewViewSet(ModelViewSet):
    queryset = StoreReview.objects.all()
    serializer_class = StoreReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return StoreReview.objects.filter(store_id=self.kwargs['store_pk'])

    def get_serializer_context(self):
        return  {'store_pk': self.kwargs['store_pk']}


class StoreRatingViewSet(ModelViewSet):
    queryset = StoreRating.objects.all()
    serializer_class = StoreRatingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return StoreRating.objects.filter(store_id=self.kwargs['store_pk'])


    def get_serializer_context(self):
        return {'store_pk': self.kwargs['store_pk']}

    def perform_create(self, serializer):
        user = self.request.user

        serializer.save()


class StoreOrdersViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        store_pk = self.kwargs.get('store_pk')
        store = get_object_or_404(Store, pk=store_pk)
        return Order.objects.filter(Store=store)





class MessageViewSet(ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # If the user is a store owner (assumed to have a related 'store' attribute)
        if hasattr(user, "store"):
            # For store owners, show messages they sent or messages sent to their store,
            # as well as messages where they are the customer recipient (if any).
            return Message.objects.filter(
                Q(sender=user) | Q(receiver_store=user.store) | Q(receiver_user=user)
            ).order_by('-timestamp')
        else:
            # For customers, show messages they sent or replies where they are the receiver.
            return Message.objects.filter(
                Q(sender=user) | Q(receiver_user=user)
            ).order_by('-timestamp')

    def perform_create(self, serializer):
        # Let the serializer use the payload provided by the front end.
        serializer.save(sender=self.request.user)



class WishListViewSet(ModelViewSet):
    serializer_class = WishListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.wishlist_set.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):

        import uuid
        payment_reference = str(uuid.uuid4())

        serializer.save(payment_reference=payment_reference, status=Payment.STATUS_PENDING)




class CartViewSet(ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user, status=Cart.STATUS_ACTIVE)

    def create(self, request, *args, **kwargs):
        default_store = get_default_store()  # Get a default store
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            status=Cart.STATUS_ACTIVE,
            store=default_store  # Provide the store to satisfy the NOT NULL constraint
        )
        serializer = self.get_serializer(cart)
        return Response(serializer.data)


class CartItemViewSet(ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter CartItem via the related cart's user and active status.
        return CartItem.objects.filter(cart__user=self.request.user, cart__status=Cart.STATUS_ACTIVE)

    def create(self, request, *args, **kwargs):
        default_store = get_default_store()  # Get the default store

        # Instead of get_or_create (which can return multiple objects), filter for existing carts.
        cart_qs = Cart.objects.filter(
            user=request.user,
            status=Cart.STATUS_ACTIVE,
            store=default_store
        )
        if cart_qs.exists():
            # If more than one exists, choose the most recent (ordered by id descending).
            cart = cart_qs.order_by('-id').first()
        else:
            cart = Cart.objects.create(
                user=request.user,
                status=Cart.STATUS_ACTIVE,
                store=default_store
            )

        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if quantity <= 0:
            return Response(
                {'error': 'Quantity must be greater than 0'},
                status=status.HTTP_400_BAD_REQUEST
            )

        product = get_object_or_404(Product, id=product_id)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity = (cart_item.quantity or 0) + quantity

        cart_item.save()

        serializer = self.get_serializer(cart_item)
        return Response(serializer.data)


from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Order, OrderItem, Cart
from .serializers import OrderSerializer

class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Find the active cart for the user.
        active_carts = Cart.objects.filter(user=request.user, status=Cart.STATUS_ACTIVE)
        if not active_carts.exists():
            return Response({"error": "No active cart found"}, status=status.HTTP_400_BAD_REQUEST)
        # If multiple active carts exist, choose the most recent one.
        cart = active_carts.order_by('-id').first()

        # Retrieve shipping details from the request.
        shipping_address = request.data.get("shipping_address")
        contact_info = request.data.get("contact_info")
        if not shipping_address or not contact_info:
            return Response(
                {"error": "Shipping address and contact info are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate the total price from the cart items.
        total_price = cart.calculate_total_price()
        if total_price == 0:
            return Response({"error": "Cart is empty. Cannot create order."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Create the Order.
        order = Order.objects.create(
            cart=cart,
            shipping_address=shipping_address,
            contact_info=contact_info,
            user=request.user,
            store=cart.store,
            total_price=total_price
        )

        # Convert each CartItem into an OrderItem.
        for cart_item in cart.cart_items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price_at_purchase=cart_item.product.unit_price,
            )

        # Optionally, mark the cart as inactive now that the order is placed.
        cart.status = Cart.STATUS_INACTIVE
        cart.save()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)




class CategoryImageViewSet(ReadOnlyModelViewSet):
    queryset = CategoryImage.objects.all()
    serializer_class = CategoryImageSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return CategoryImage.objects.filter(category_id=self.kwargs['category_pk'])

    def get_serializer_context(self):
        return {'category_pk': self.kwargs['category_pk']}


@csrf_exempt
def upload_store_logo(request):

    if request.method == "POST" and request.FILES.get("image") and request.POST.get("store_id"):
        store_id = request.POST.get("store_id")
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return JsonResponse({"success": False, "error": "Store not found."}, status=404)

        image = request.FILES["image"]
        temp_path = f"/tmp/{image.name}"
        with open(temp_path, "wb") as f:
            for chunk in image.chunks():
                f.write(chunk)

        # Use a dedicated bucket for store logos, e.g., "store-logos"
        public_url = upload_to_supabase(temp_path, bucket_key="store-logos")
        os.remove(temp_path)

        if public_url:
            store.logo = public_url
            store.save()
            return JsonResponse({"success": True, "store_id": store.id, "logo": public_url})
        else:
            return JsonResponse({"success": False, "error": "Upload failed."}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)


@csrf_exempt
def upload_category_image(request):
    """
    Expects a POST with:
      - category_id (in POST data)
      - image file under key "image"
    """
    if request.method == "POST" and request.FILES.get("image") and request.POST.get("category_id"):
        category_id = request.POST.get("category_id")
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return JsonResponse({"success": False, "error": "Category not found."}, status=404)

        image = request.FILES["image"]
        temp_path = f"/tmp/{image.name}"
        with open(temp_path, "wb") as f:
            for chunk in image.chunks():
                f.write(chunk)

        # Use a dedicated bucket for category images, e.g., "category-images"
        public_url = upload_to_supabase(temp_path, bucket_key="category-images")
        os.remove(temp_path)

        if public_url:
            category_image = CategoryImage.objects.create(category=category, image=public_url)
            return JsonResponse({"success": True, "category_image_id": category_image.id, "image": public_url})
        else:
            return JsonResponse({"success": False, "error": "Upload failed."}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)


@csrf_exempt
def upload_hero_image(request):
    """
    Expects a POST with:
      - Optional: title, description in POST data
      - Image file under key "image"
    """
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]
        title = request.POST.get("title", "")
        description = request.POST.get("description", "")

        temp_path = f"/tmp/{image.name}"
        with open(temp_path, "wb") as f:
            for chunk in image.chunks():
                f.write(chunk)

        # Use a dedicated bucket for hero images, e.g., "hero-images"
        public_url = upload_to_supabase(temp_path, bucket_key="hero-images")
        os.remove(temp_path)

        if public_url:
            hero_image = HeroImage.objects.create(title=title, description=description, image=public_url)
            return JsonResponse({"success": True, "hero_image_id": hero_image.id, "image": public_url})
        else:
            return JsonResponse({"success": False, "error": "Upload failed."}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)


@csrf_exempt
def upload_product_image(request):
    """
    Expects a POST with:
      - product_id (in POST data)
      - image file under key "image"
    """
    if request.method == "POST" and request.FILES.get("image") and request.POST.get("product_id"):
        product_id = request.POST.get("product_id")
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({"success": False, "error": "Product not found."}, status=404)

        image = request.FILES["image"]
        temp_path = f"/tmp/{image.name}"
        with open(temp_path, "wb") as f:
            for chunk in image.chunks():
                f.write(chunk)

        # Use a dedicated bucket for product images, e.g., "product-images"
        public_url = upload_to_supabase(temp_path, bucket_key="product-images")
        os.remove(temp_path)

        if public_url:
            product_image = ProductImage.objects.create(product=product, image=public_url)
            return JsonResponse({"success": True, "product_image_id": product_image.id, "image": public_url})
        else:
            return JsonResponse({"success": False, "error": "Upload failed."}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)