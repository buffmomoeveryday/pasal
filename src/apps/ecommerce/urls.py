from django.urls import path
from .views import (
    store_front,
    register_customer,
    login_customer,
    logout_customer,
    add_to_cart,
    about_us,
    cart,
    orders,
    delete_cart_item,
    products,
    product_detail,
    create_checkout_session,
    checkout_success,
    checkout_cancel,
    search_product,
    settings,
)

from .views import htmx_get_cart_quantity
from .webhooks import stripe_webhook_payment_success

urlpatterns = [
    path(
        "",
        store_front,
        name="store-front",
    ),
    path(
        "product/<slug:product_slug>/",
        product_detail,
        name="product-detail",
    ),
    path(
        "register/customer",
        register_customer,
        name="register-customer",
    ),
    path(
        "login/customer",
        login_customer,
        name="login-customer",
    ),
    path(
        "logout/customer",
        logout_customer,
        name="logout-customer",
    ),
    path(
        "add_to_cart/<slug:product_slug>",
        add_to_cart,
        name="add-to-cart",
    ),
    path(
        "cart",
        cart,
        name="view_cart",
    ),
    path(
        "get/cart_count",
        htmx_get_cart_quantity,
        name="htmx-get-cart-count",
    ),
    path(
        "delete_cart_item/<int:cart_item_id>/",
        delete_cart_item,
        name="delete-cart-item",
    ),
    path(
        "about-us",
        about_us,
        name="about-us",
    ),
    path(
        "products",
        products,
        name="products",
    ),
    path(
        "orders",
        orders,
        name="orders",
    ),
    path(
        "customer-settings",
        settings,
        name="customer_settings",
    ),
]


_htmx = [
    path(
        "search-product",
        search_product,
        name="search-product",
    )
]


stripe = [
    path(
        "checkout",
        create_checkout_session,
        name="stripe-checkout-session",
    ),
    path(
        "success",
        checkout_success,
        name="stripe-checkout-success",
    ),
    path(
        "cancel",
        checkout_cancel,
        name="stripe-checkout-cancel",
    ),
]

stripe_webhooks = [
    path(
        "webhooks/success",
        stripe_webhook_payment_success,
        name="webhooks_success",
    )
]

urlpatterns += _htmx
urlpatterns += stripe
urlpatterns += stripe_webhooks
