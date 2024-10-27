from django.contrib import admin

from .models import (
    ProductCategory,
    ProductImages,
    Products,
    Cart,
    Customer,
    CartItem,
    Order,
    OrderItem,
)
from django.contrib.auth.admin import UserAdmin as BaseCustomserAdmin


from .models import (
    FeaturedProductsUI,
    FooterUI,
    TopBarUI,
    RelatedProductsUI,
    ImageWithTextUI,
)


class CustomserAdmin(BaseCustomserAdmin):
    model = Customer
    ordering = ["email"]


admin.site.register(Customer)
admin.site.register(Products)

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)

# UI
admin.site.register(ProductImages)
admin.site.register(ProductCategory)
admin.site.register(TopBarUI)
admin.site.register(FooterUI)
admin.site.register(FeaturedProductsUI)
admin.site.register(RelatedProductsUI)
admin.site.register(ImageWithTextUI)
