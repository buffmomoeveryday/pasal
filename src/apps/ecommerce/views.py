import stripe
from django_htmx.http import HttpResponseClientRefresh
import re

from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.db.models import Q

from apps.ecommerce.decorators import login_customer_required

from apps.ecommerce.forms import CustomerLoginForm

from apps.tenant.models import StoreInformation
from apps.ecommerce.models import (
    Products,
    Customer,
    ProductCategory,
    Order,
    CartItem,
    Cart,
    TopBarUI,
    ImageWithTextUI,
    FeaturedProductsUI,
    FooterUI,
)


stripe.api_key = settings.STRIPE_SECRET_KEY


def store_front(request):
    tenant = request.tenant
    if not request.tenant:
        return redirect(reverse_lazy("pasal_home"))
    products = Products.objects.filter(tenant=tenant)
    topbar = TopBarUI.objects.filter(tenant=tenant).first()
    image_with_text = ImageWithTextUI.objects.filter(tenant=tenant).first()
    featured_products = FeaturedProductsUI.objects.filter(tenant=tenant)
    information = StoreInformation.objects.filter(tenant=tenant).first()
    footer_ui = FooterUI.objects.filter(tenant=tenant).first()

    context = {
        "tenant": tenant,
        "products": products,
        "topbar": topbar,
        "image_with_text": image_with_text,
        "featured_products": featured_products,
        "information": information,
        "footer_ui": footer_ui,
    }
    return render(
        request=request,
        template_name="ecommerce_store_front.html",
        context=context,
    )


# def register_customer(request):
#     tenant = request.tenant
#     topbar_ui = TopBarUI.objects.select_related("tenant").get(tenant=tenant)
#     information = StoreInformation.objects.filter(tenant=tenant).first()
#     footer_ui = FooterUI.objects.filter(tenant=tenant).first()

#     if request.POST:
#         first_name = request.POST.get("first_name")
#         last_name = request.POST.get("last_name")
#         email = request.POST.get("email")
#         mobile_number = request.POST.get("mobile_number")
#         password = request.POST.get("password")
#         address = request.POST.get("address")
#         tenant = tenant

#         if not re.match(r"^\d{10}$", mobile_number):
#             messages.error(
#                 request=request,
#                 message="Mobile number should be a 10-digit number.",
#             )

#             context = {
#                 "topbar": topbar_ui,
#                 "footer_ui": footer_ui,
#                 "information": information,
#             }
#             return render(
#                 request=request,
#                 template_name="ecommerce_client_registration.html",
#                 context=context,
#             )

#         try:
#             customer = Customer.objects.create(
#                 first_name=first_name,
#                 last_name=last_name,
#                 email=email,
#                 password=password,
#                 tenant=tenant,
#                 mobile_number=mobile_number,
#                 address=address,
#             )
#             stripe_customer = stripe.Customer.create(
#                 name=f"{first_name} {last_name}",
#                 email=email,
#                 stripe_account=request.tenant.stripe_id,
#                 metadata={
#                     "customer_id": customer.id,
#                     "tenant": tenant.id,
#                 },
#             )
#             customer.stripe_id = stripe_customer.id
#             customer.save()

#             messages.success(
#                 request=request,
#                 message="Successfully Created your account",
#             )

#         except Exception as e:
#             print(e)
#             messages.error(request=request, message=f"An Error Occurred {e}")
#             context = {
#                 "topbar": topbar_ui,
#                 "footer_ui": footer_ui,
#                 "information": information,
#             }
#             return render(
#                 template_name="ecommerce_client_registration.html",
#                 request=request,
#                 context=context,
#             )

#     context = {
#         "topbar": topbar_ui,
#         "footer_ui": footer_ui,
#         "information": information,
#     }


#     return render(
#         request=request,
#         template_name="ecommerce_client_registration.html",
#         context=context,
#     )
def register_customer(request):
    tenant = request.tenant
    topbar_ui = TopBarUI.objects.select_related("tenant").get(tenant=tenant)
    information = StoreInformation.objects.filter(tenant=tenant).first()
    footer_ui = FooterUI.objects.filter(tenant=tenant).first()

    if request.POST:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        mobile_number = request.POST.get("mobile_number")
        password = request.POST.get("password")
        address = request.POST.get("address")
        tenant = tenant

        if not re.match(r"^\d{10}$", mobile_number):
            messages.error(
                request=request,
                message="Mobile number should be a 10-digit number.",
            )

            context = {
                "topbar": topbar_ui,
                "footer_ui": footer_ui,
                "information": information,
            }
            return render(
                request=request,
                template_name="ecommerce_client_registration.html",
                context=context,
            )

        existing_customer = Customer.objects.filter(email=email, tenant=tenant).first()

        if existing_customer:
            messages.error(
                request=request,
                message="A user with this email already exists.",
            )
            context = {
                "topbar": topbar_ui,
                "footer_ui": footer_ui,
                "information": information,
            }
            return render(
                request=request,
                template_name="ecommerce_client_registration.html",
                context=context,
            )

        # Create customer if not exists
        customer = Customer.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            tenant=tenant,
            mobile_number=mobile_number,
            address=address,
        )
        stripe_customer = stripe.Customer.create(
            name=f"{first_name} {last_name}",
            email=email,
            stripe_account=request.tenant.stripe_id,
            metadata={
                "customer_id": customer.id,
                "tenant": tenant.id,
            },
        )
        customer.stripe_id = stripe_customer.id
        customer.save()

        messages.success(
            request=request,
            message="Successfully Created your account",
        )

    context = {
        "topbar": topbar_ui,
        "footer_ui": footer_ui,
        "information": information,
    }

    return render(
        request=request,
        template_name="ecommerce_client_registration.html",
        context=context,
    )


def login_customer(request):
    tenant = request.tenant
    topbar_ui = TopBarUI.objects.select_related("tenant").get(tenant=tenant)
    information = StoreInformation.objects.filter(tenant=tenant).first()
    footer_ui = FooterUI.objects.filter(tenant=tenant).first()

    if request.method == "POST":
        form = CustomerLoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            try:
                customer = Customer.objects.get(email=email, tenant=tenant)

            except Customer.DoesNotExist:
                messages.error(request=request, message="Invalid Login Credentials")
                return render(
                    request,
                    "ecommerce_client_login.html",
                    {
                        "form": form,
                        "topbar": topbar_ui,
                        "footer_ui": footer_ui,
                        "information": information,
                    },
                )

            if password == customer.password:
                request.session["customer_id"] = customer.id
                messages.success(request=request, message="Logged in Successfully")
                return redirect("store-front")
            else:
                messages.error(request=request, message="Invalid Login Credentials")
                return render(
                    request,
                    "ecommerce_client_login.html",
                    {"form": form},
                )
        else:
            return render(
                request,
                "ecommerce_client_login.html",
                {
                    "form": form,
                    "topbar": topbar_ui,
                    "footer_ui": footer_ui,
                    "information": information,
                },
            )

    else:
        form = CustomerLoginForm()

    return render(
        request,
        "ecommerce_client_login.html",
        {
            "form": form,
            "topbar": topbar_ui,
            "footer_ui": footer_ui,
            "information": information,
        },
    )


def about_us(request):
    tenant = request.tenant

    topbar_ui = TopBarUI.objects.select_related("tenant").get(tenant=tenant)
    footer_ui = FooterUI.objects.filter(tenant=tenant).first()

    information = StoreInformation.objects.get(tenant=request.tenant)

    context = {
        "information": information,
        "topbar": topbar_ui,
        "footer_ui": footer_ui,
    }
    return render(
        request=request,
        template_name="ecommerce_about_us.html",
        context=context,
    )


def products(request):
    tenant = request.tenant

    products = Products.objects.filter(tenant=tenant)
    categories = ProductCategory.objects.filter(tenant=tenant)
    topbar_ui = TopBarUI.objects.select_related("tenant").get(tenant=tenant)
    information = StoreInformation.objects.filter(tenant=tenant).first()
    footer_ui = FooterUI.objects.filter(tenant=tenant).first()

    context = {
        "topbar": topbar_ui,
        "footer_ui": footer_ui,
        "information": information,
        "products": products,
        "categories": categories,
    }
    return render(
        request=request,
        template_name="ecommerce_product_list.html",
        context=context,
    )


@login_customer_required
def logout_customer(request):
    if "customer_id" in request.session:
        del request.session["customer_id"]
        messages.success(request=request, message="Logged out Successfully")
    return redirect("store-front")


def product_detail(request, product_slug):
    tenant = request.tenant
    product = get_object_or_404(Products, tenant=tenant, slug=product_slug)

    topbar_ui = get_object_or_404(TopBarUI, tenant=tenant)
    information = get_object_or_404(StoreInformation, tenant=tenant)
    footer_ui = get_object_or_404(FooterUI, tenant=tenant)

    return render(
        request=request,
        template_name="partials/ecommerce_product_detail.html",
        context={
            "topbar": topbar_ui,
            "footer_ui": footer_ui,
            "information": information,
            "product": product,
        },
    )


@login_customer_required
@require_http_methods(["GET"])
def add_to_cart(request, product_slug):
    if request.htmx:
        quantity = int(request.GET.get("quantity"))
        product = get_object_or_404(Products, slug=product_slug)
        customer = request.customer
        cart = Cart.objects.get_or_create(
            cart_customer=customer, tenant=request.tenant
        )[0]

        if product.stock_quantity < quantity:
            messages.error(
                request=request,
                message="Cannot add more to cart. Stock quantity limit reached.",
            )
            return HttpResponseClientRefresh()

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            total_quantity = cart_item.quantity + quantity
            if total_quantity > product.stock_quantity:
                messages.error(
                    request=request,
                    message="Cannot add more to cart. Stock quantity limit reached.",
                )
                return HttpResponseClientRefresh()
            else:
                cart_item.quantity = total_quantity
                cart_item.save()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        cart.items.add(cart_item)

        messages.success(request=request, message="Successfully added to cart.")
        return HttpResponseClientRefresh()


@login_customer_required
def cart(request):
    tenant = request.tenant
    topbar_ui = TopBarUI.objects.select_related("tenant").get(tenant=tenant)
    information = StoreInformation.objects.filter(tenant=tenant).first()
    footer_ui = FooterUI.objects.filter(tenant=tenant).first()
    try:
        cart = Cart.objects.get(cart_customer=request.customer, tenant=tenant)
    except Exception as e:
        cart = Cart.objects.create(cart_customer=request.customer, tenant=tenant)

    context = {
        "cart": cart,
        "topbar": topbar_ui,
        "footer_ui": footer_ui,
        "information": information,
    }

    return render(
        request=request,
        template_name="ecommerce_cart.html",
        context=context,
    )


@login_customer_required
@require_http_methods(["GET"])
def delete_cart_item(request, cart_item_id):
    if request.htmx:
        cart_item = get_object_or_404(CartItem, id=cart_item_id)
        cart = None
        for c in Cart.objects.filter(items=cart_item):
            if c.cart_customer == request.customer:
                cart = c
                break
        if cart:
            cart.items.remove(cart_item)
            messages.success(request=request, message="Cart item deleted successfully.")
            return HttpResponseClientRefresh()
        else:
            messages.error(
                request=request,
                message="You are not authorized to delete this cart item.",
            )
            return HttpResponseClientRefresh()
    else:
        return HttpResponseBadRequest("This endpoint only supports HTMX requests.")


@login_customer_required
@require_http_methods(["GET"])
def htmx_get_cart_quantity(request):
    try:
        if request.htmx:
            cart = Cart.objects.get(
                tenant=request.tenant, cart_customer=request.customer
            )
            context = {"cart_items_count": cart.total_products()}
            return render(
                request=request,
                template_name="partials/ecommerce_cart_icon.html",
                context=context,
            )
    except Cart.DoesNotExist:
        context = {"cart_items_count": 0}
        return render(
            request=request,
            template_name="partials/ecommerce_cart_icon.html",
            context=context,
        )


# stripe
@csrf_exempt
@login_customer_required
def create_checkout_session(request):
    cart = Cart.objects.get(tenant=request.tenant, cart_customer=request.customer)

    for cart_item in cart.items.all():
        if cart_item.quantity > cart_item.product.stock_quantity:
            messages.error(
                request=request,
                message=f"Cannot proceed to checkout. Stock quantity limit reached for {cart_item.product.name}.",
            )
            return redirect("view_cart")

    line_items = cart.generate_stripe_line_items()

    success_url = f"http://{request.tenant.subdomain}.localhost:8000/success"
    cancel_url = f"http://{request.tenant.subdomain}.localhost:8000/cancel"

    if not isinstance(line_items, list):
        raise ValueError("Line items should be a list")

    try:
        checkout_session = stripe.checkout.Session.create(
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            line_items=line_items,
            customer=request.customer.stripe_id,
            stripe_account=request.tenant.stripe_id,
        )
        return redirect(checkout_session.url, code=303)

    except Cart.DoesNotExist:
        return HttpResponse("Cart not found", status=404)

    except ValueError as ve:
        return HttpResponse(str(ve), status=400)

    except Exception as e:
        return HttpResponse(f"An error occurred {e}", status=500)


@login_customer_required
def checkout_success(reqeust):
    return redirect(reverse_lazy("orders"))


@login_customer_required
def checkout_cancel(request):
    return redirect(reverse_lazy("view_cart"))


@login_customer_required
def orders(request):

    tenant = request.tenant
    topbar_ui = TopBarUI.objects.select_related("tenant").get(tenant=tenant)
    information = StoreInformation.objects.filter(tenant=tenant).first()
    footer_ui = FooterUI.objects.filter(tenant=tenant).first()

    orders = Order.objects.filter(order_customer=request.customer)

    context = {
        "orders": orders,
        "topbar": topbar_ui,
        "footer_ui": footer_ui,
        "information": information,
    }
    return render(
        request=request,
        template_name="ecommerce_list_orders.html",
        context=context,
    )


def search_product(request):
    if request.POST:
        tenant = request.tenant
        search = request.POST.get("search")
        products = Products.objects.filter(
            Q(tenant=tenant)
            & (Q(name__icontains=search) | Q(description__icontains=search))
        )

        if products:
            context = {"products": products}

            return render(
                request=request,
                template_name="ecommerce_product_list.html#products",
                context=context,
            )

        else:

            return HttpResponse(f"No Product named {search}")


# views.py
from django.shortcuts import render, redirect
from .forms import CustomerUpdateForm


def settings(request):

    tenant = request.tenant
    topbar_ui = TopBarUI.objects.select_related("tenant").get(tenant=tenant)
    information = StoreInformation.objects.filter(tenant=tenant).first()
    footer_ui = FooterUI.objects.filter(tenant=tenant).first()

    customer = request.customer
    if request.method == "POST":
        form = CustomerUpdateForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request=request, message="Edited Successfully")
            return redirect("customer_settings")
        else:
            form = CustomerUpdateForm(request.POST, instance=customer)
            messages.error(request=request, message="Error")
            return redirect(reverse_lazy("customer_settings"))
    else:
        form = CustomerUpdateForm(instance=customer)

    return render(request, "ecommerce_customer_settings.html", {"form": form})
