import random
import uuid
import string


from django.db import models
from django.db.models import Sum

from django.core.exceptions import ValidationError
from django.utils.text import slugify

from apps.tenant.models import TenantAwareModel


class Customer(TenantAwareModel):
    first_name = models.CharField(max_length=244)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    stripe_id = models.CharField(max_length=255, default=None, null=True)

    # def save(self, *args, **kwargs):
    #     existing_customer = (
    #         Customer.objects.filter(email=self.email).exclude(pk=self.pk).first()
    #     )

    #     if existing_customer:
    #         raise ValidationError("Customer with this email already exists.")
    #     else:
    #         super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tenant.name}'s Customer : {self.first_name}"


# CORE
class ProductImages(TenantAwareModel):
    images = models.ImageField(verbose_name="Product Images")

    def __str__(self):
        return f"{self.tenant.name}: {self.images.name}"


class ProductCategory(TenantAwareModel):
    name = models.CharField(verbose_name="Category", max_length=255)

    def __str__(self):
        return f"{self.tenant.name}:{self.name}"


class Products(TenantAwareModel):
    name = models.CharField(
        verbose_name="Product Name",
        max_length=255,
    )
    price = models.DecimalField(
        verbose_name="Product Price",
        max_digits=15,
        decimal_places=2,
    )  # done
    cost_price = models.DecimalField(
        verbose_name="Cost Price", max_digits=15, decimal_places=2, default=0
    )  # done

    discount = models.DecimalField(
        verbose_name="Discount",
        max_digits=15,
        decimal_places=2,
    )  # done
    stock_quantity = models.PositiveIntegerField(
        default=0, verbose_name="Stock Quantity"
    )  # done
    images = models.ManyToManyField(ProductImages)

    category = models.ManyToManyField(
        to=ProductCategory,
    )  # done

    description = models.TextField(
        verbose_name="Product Description",
    )

    slug = models.SlugField(unique=True, blank=True)

    @property
    def stock(self):
        if self.stock_quantity > 0:
            return self.stock_quantity
        else:
            return None

    @property
    def margin(self):
        margin = self.price - self.cost_price
        return margin

    def __str__(self):
        return f"{self.tenant.name}:{self.name}"

    def save(self, *args, **kwargs):
        if not self.slug or self.name != getattr(self, "_original_name", None):
            self._original_name = self.name
            base_slug = slugify(self.name)

            # Check if the object is being created (not yet in the database)
            if not self.pk:
                slug_exists = Products.objects.filter(slug=base_slug).exists()

                if slug_exists:
                    random_suffix = "".join(
                        random.choices(string.ascii_letters + string.digits, k=6)
                    )
                    self.slug = f"{base_slug}-{random_suffix}"
                else:
                    self.slug = base_slug

        super().save(*args, **kwargs)


class CartItem(models.Model):
    product = models.ForeignKey(
        Products, on_delete=models.CASCADE, blank=True, null=True
    )
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.product.price * self.quantity


class Cart(TenantAwareModel):
    cart_customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, null=True, blank=True
    )
    items = models.ManyToManyField(CartItem)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def total(self):
        return sum(item.subtotal() for item in self.items.all())

    def total_products(self):
        return self.items.count()

    def generate_stripe_line_items(self):
        line_items = []
        for cart_item in self.items.all():
            line_item = {
                "price_data": {
                    "currency": "aud",
                    "unit_amount": int(cart_item.product.price * 100),
                    "product_data": {
                        "name": cart_item.product.name,
                        "description": cart_item.product.description,
                    },
                },
                "quantity": cart_item.quantity,
            }
            line_items.append(line_item)
        return line_items

    def __str__(self):
        return f"{self.tenant.name}:{self.cart_customer.email}"


class OrderItem(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=15, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price


class Order(TenantAwareModel):
    status_choices = (
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    )
    order_customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, null=True, blank=True
    )
    items = models.ManyToManyField(OrderItem)  # Change here
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=status_choices, default="PENDING")
    order_number = models.CharField(max_length=36, unique=True)

    # Additional fields for shipping information, billing information, etc.
    # Add fields as per your requirement

    def generate_unique_order_number(self):
        unique_order_number = str(uuid.uuid4())
        while Order.objects.filter(order_number=unique_order_number).exists():
            unique_order_number = str(uuid.uuid4())
        return unique_order_number

    def total_amount(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"{self.tenant.name}:{self.order_customer.email}"


# UI
class RelatedProductsUI(TenantAwareModel):
    related_products = models.ManyToManyField(
        to=Products,
        verbose_name="Related Products",
    )

    def __str__(self):
        return f"{self.tenant.name} - {self.related_products}"


class FooterUI(TenantAwareModel):
    instagram = models.URLField(null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.tenant.name} : Socials"


class TopBarUI(TenantAwareModel):
    text = models.TextField()

    def __str__(self) -> str:
        return f"{self.tenant.name}:topbar"


class ImageWithTextUI(TenantAwareModel):
    overlay_image = models.ImageField()
    overlay_text = models.CharField(max_length=255, verbose_name="Text Image Overlay")


class CategoryUI(TenantAwareModel):
    category = models.ForeignKey(
        to=ProductCategory,
        verbose_name="Category to show",
        on_delete=models.SET_NULL,
        null=True,
    )

    def __str__(self):
        return f"{self.tenant.name}:categoryUI"


class FeaturedProductsUI(TenantAwareModel):
    products = models.ManyToManyField(to=Products, verbose_name="Featured Products")

    def __str__(self):
        return f"{self.tenant.name}:featuredProductsUI"
