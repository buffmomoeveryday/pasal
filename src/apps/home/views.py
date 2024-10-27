import time
import json

import stripe
from django_htmx.http import HttpResponseClientRefresh
import plotly.graph_objs as go

from django.utils.numberformat import format as format_number
from django.urls import reverse_lazy
from django.conf import settings
from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Q, F
from apps.home.utils import format_number, convert_unix_to_local

from apps.home.forms import (
    FooterUIForm,
    TopBarUIForm,
    ImageWithTextUIForm,
    FeaturedProductsUIForm,
    EditProduct,
    AddStoreInformation,
    CustomUser,
    LoginForm,
    CreateProductImage,
    CreateCategory,
    CreateProductForm,
    EmployeeRegisterForm,
    CustomUserEditForm,
)
from apps.ecommerce.models import (
    TopBarUI,
    FooterUI,
    FeaturedProductsUI,
    ImageWithTextUI,
    Products,
    Customer,
    ProductImages,
    Order,
    OrderItem,
)

from apps.tenant.models import StoreInformation, Employees, Tenant
from apps.tenant.decorators import root_only, login_required_tenant
from apps.tenant.utils import redirect_after_login


stripe.api_key = settings.STRIPE_SECRET_KEY
current_time = int(time.time())


# pasal home
@root_only
def pasal_home(request):
    return render(request=request, template_name="tenant_landing.html")


@root_only
def pasal_tac(request):
    return render(request=request, template_name="tenant_tac.html")


# register user
@root_only
def pasal_register(request):
    if request.POST:
        email = request.POST.get("email")
        store_name = request.POST.get("store_name")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        phone_number = request.POST.get("phone_number")
        # registered_address = request.POST.get("registered_address")

        # Check if passwords match
        if password != password_confirm:
            messages.error(
                request=request,
                message="The Two Passwords Don't Match",
            )
            return render(
                request=request,
                template_name="tenant_register.html",
            )

        # Check if phone number contains only digits
        if not phone_number.isdigit():
            messages.error(
                request=request,
                message="Phone number must contain only digits.",
            )
            return render(
                request=request,
                template_name="tenant_register.html",
            )

        try:
            CustomUser.objects.get(email=email)
            messages.error(
                request=request,
                message="Email already exists.",
            )
            return render(
                request=request,
                template_name="tenant_register.html",
            )
        except ObjectDoesNotExist:
            pass

        try:
            Tenant.objects.get(name=store_name)
            messages.error(
                request=request,
                message="Store name already exists.",
            )
            return render(
                request=request,
                template_name="tenant_register.html",
            )
        except ObjectDoesNotExist:
            pass

        user = CustomUser.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )
        user.save()

        tenant = Tenant.objects.create(
            name=store_name,
            subdomain=str(store_name).lower(),
        )
        tenant.save()

        employee = Employees.objects.create(
            user=user,
            tenant=tenant,
            is_owner=True,
        )
        employee.save()
        messages.success(
            request=request,
            message="Created successfully",
        )

        tenant_account = stripe.Account.create(
            type="custom",
            country="AU",
            email=email,
            business_type="individual",
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
            individual={
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": "000-000-0000",
                "id_number": "000000000",
                "dob": {
                    "day": 1,
                    "month": 1,
                    "year": 1901,
                },
                "address": {
                    "line1": "address_full_match",
                    "postal_code": "6450",
                    "city": " Pink Lake",
                    "state": "Western Australia",
                },
            },
        )

        tenant.stripe_id = tenant_account["id"]
        tenant.save()

        stripe.Account.modify(
            tenant_account["id"],
            tos_acceptance={
                "date": current_time,
                "ip": request.META.get("REMOTE_ADDR", "0.0.0.0"),
            },
            business_profile={
                "url": "https://accessible.stripe.com",
                "mcc": "5734",
            },
        )

        bank_account_params = {
            "object": "bank_account",
            "country": "AU",
            "currency": "AUD",
            "account_holder_name": "John Doe",  # Replace with the account holder's name
            "account_holder_type": "individual",
            "routing_number": "110000",  # Replace with the routing number
            "account_number": "000123456",  # Replace with the account number
        }

        # Create bank account
        bank_account = stripe.Account.create_external_account(
            tenant_account["id"], external_account=bank_account_params
        )

        return render(
            request=request,
            template_name="tenant_register.html",
        )

    return render(
        request=request,
        template_name="tenant_register.html",
    )


# dashboard
@root_only
def pasal_dashboard_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(
                request,
                email=email,
                password=password,
            )
            if user is not None:
                login(request, user)
                return redirect_after_login(request=request)
            else:
                form.add_error(None, "Invalid credentials")
    else:
        form = LoginForm()
    context = {"form": form}
    return render(
        request=request, template_name="dashboard/tenant_login.html", context=context
    )


@root_only
@login_required_tenant
def pasal_dashboard(request):
    tenant = Employees.objects.get(user=request.user).tenant
    context = {"tenant": tenant}
    return render(
        request=request,
        template_name="dashboard/tenant_dashboard.html",
        context=context,
    )


@root_only
@login_required_tenant
def pasal_dashboard_total_sales(request):

    tenant = Employees.objects.get(user=request.user).tenant
    try:
        all_orders = Order.objects.filter(tenant=tenant)
        total_amount = sum(order.total_amount() for order in all_orders)
        return HttpResponse(f"${format_number(total_amount)}")

    except Exception as e:
        return HttpResponse(f"Error {e}")


@root_only
@login_required_tenant
def pasal_dashboard_average_order_value(request):

    tenant = Employees.objects.get(user=request.user).tenant
    total_orders = Order.objects.filter(tenant=tenant).count()

    try:
        all_orders = Order.objects.filter(tenant=tenant)
        total_amount = sum(order.total_amount() for order in all_orders)
        num_orders = int(total_orders)

        if num_orders == 0:
            average_order_value = 0
            return HttpResponse(f"${average_order_value}")

        average_order_value = total_amount / num_orders
        return HttpResponse(f"${format_number(round(average_order_value,2))}")

    except stripe.error.StripeError as e:
        return HttpResponse("Stripe Error")


def calculate_total_amount(order):
    return sum(item.price for item in order.items.all())


from django.db.models import ExpressionWrapper, DecimalField
from django.template.loader import render_to_string


from django.http import HttpResponse
from django.db.models import Sum, F
from django.template.loader import render_to_string


@root_only
@login_required_tenant
def pasal_dashboard_top_customer(request):
    top_customer = (
        Order.objects.values("order_customer")
        .filter(tenant=request.tenant)
        .annotate(total_amount=Sum(F("items__quantity") * F("items__price")))
        .order_by("-total_amount")
        .first()
    )
    if top_customer:
        customer_id = top_customer["order_customer"]
        customer = Customer.objects.get(pk=customer_id)
        total_amount = top_customer["total_amount"]
        context = {
            "customer": f"{customer.first_name} {customer.last_name}",
            "total_amount": total_amount,
        }
        html = f"""
        <p id="customer_name">{context['customer']}</p>
        <p id="customer_total_purchase">${context['total_amount']}</p>
        """
        return HttpResponse(html)
    else:
        html = f"""
        <p id="customer_name">No Top Customers Found</p>
        <p id="customer_total_purchase">$0</p>
        """
        return HttpResponse(html)


@root_only
@login_required_tenant
def pasal_dashboard_top_selling_products(request):
    tenant = Employees.objects.get(user=request.user).tenant

    # top_product = (
    #     OrderItem.objects.values("product")
    #     .annotate(total_quantity=Sum("quantity"))
    #     .order_by("-total_quantity")
    #     .first()
    # )

    top_product = (
        OrderItem.objects.filter(
            order__tenant=tenant
        )  # Filtering orders by the current tenant
        .values("product")
        .annotate(total_quantity=Sum("quantity"))
        .order_by("-total_quantity")
        .first()
    )

    if top_product:
        product_id = top_product["product"]
        product = Products.objects.get(pk=product_id)
        total_quantity = top_product["total_quantity"]
        top_product_data = {
            "product_name": product.name,
            "total_quantity": total_quantity,
        }
        html = f"""
        <p id="product_name">{top_product_data['product_name']}</p>
        <p id="product_quantity">{top_product_data['total_quantity']}</p>
        """

        return HttpResponse(html)

    else:
        html = f"""
        <p id="product_name">No Products Sold</p>
        <p id="product_quantity">0</p>
        """

        return HttpResponse(html)


@root_only
@login_required_tenant
def pasal_dashboard_total_customers(request):
    tenant = Employees.objects.get(user=request.user).tenant
    total_customers = Customer.objects.filter(tenant=tenant).count()
    customers = format_number(total_customers)
    return HttpResponse(customers)


@root_only
@login_required_tenant
def pasal_dashboard_total_orders(request):
    tenant = Employees.objects.get(user=request.user).tenant
    total_orders = Order.objects.filter(tenant=tenant).count()
    orders = format_number(total_orders)
    return HttpResponse(orders)


@root_only
@login_required_tenant
def pasal_dashboard_transactions_list(request):
    tenant = Employees.objects.get(user=request.user).tenant
    stripe_account_id = tenant.stripe_id

    try:
        payment_intent = stripe.PaymentIntent.list(stripe_account=stripe_account_id)

        transaction_list = []
        for transaction in payment_intent.data:
            transaction_list.append(
                {
                    "id": transaction.id,
                    "amount": format_number(int(transaction.amount) / 100),
                    "currency": transaction.currency,
                    "customer": Customer.objects.get(stripe_id=transaction.customer),
                    "date": convert_unix_to_local(transaction.created),
                }
            )
        context = {
            "transactions": transaction_list,
        }
        return render(
            request,
            "dashboard/tenant_dashboard.html#transaction",
            context=context,
        )
    except stripe.error.StripeError as e:
        return HttpResponse({"error": str(e)})


@root_only
@login_required_tenant
def pasal_chart_sales_report(request):
    tenant = Employees.objects.get(user=request.user).tenant
    connect_account = tenant.stripe_id

    charges = stripe.Charge.list(
        expand=["data.customer"],
        api_key=stripe.api_key,
        stripe_account=connect_account,
    )

    from datetime import datetime

    sales_by_date = {}
    for charge in charges.data:
        date = datetime.utcfromtimestamp(charge.created).strftime("%Y-%m-%d")
        amount = charge.amount / 100
        if date not in sales_by_date:
            sales_by_date[date] = 0
        sales_by_date[date] += amount

    sorted_sales = sorted(sales_by_date.items())

    return JsonResponse({"sales": sorted_sales})


@root_only
@login_required_tenant
def pasal_chart_category_sales_report(request):
    tenant = Employees.objects.get(user=request.user).tenant
    category_data = {}

    orders = Order.objects.filter(tenant=tenant)

    for order in orders:
        for item in order.items.all():
            for category in item.product.category.all():
                category_name = category.name

                if category_name in category_data:
                    category_data[category_name] += item.quantity
                else:
                    category_data[category_name] = item.quantity

    labels = list(category_data.keys())
    values = list(category_data.values())

    return JsonResponse({"category_data": {"labels": labels, "values": values}})


@root_only
@login_required_tenant
def pasal_dashboard_order(request):
    tenant = Employees.objects.get(user=request.user).tenant
    orders = Order.objects.filter(tenant=tenant)
    context = {"orders": orders}
    print(orders)
    return render(
        request=request,
        template_name="dashboard/tenant_dashboard.html#orders",
        context=context,
    )


@root_only
@login_required_tenant
def pasal_dashboard_sales(request):
    tenant = Employees.objects.get(user=request.user).tenant
    context = {"tenant": tenant}
    return render(
        request=request, template_name="dashboard/tenant_sales.html", context=context
    )


@root_only
@login_required_tenant
def pasal_dashboard_logout(request):
    logout(request)
    return redirect("pasal-dashboard-login")


# store information
@root_only
@login_required_tenant
def pasal_ui_storefront_layout(request):
    tenant = Employees.objects.get(user=request.user).tenant

    products_exists = Products.objects.filter(tenant=tenant).exists()

    footer_form = FooterUIForm(instance=FooterUI.objects.filter(tenant=tenant).first())
    topbar_form = TopBarUIForm(instance=TopBarUI.objects.filter(tenant=tenant).first())
    image_with_text_form = ImageWithTextUIForm(
        instance=ImageWithTextUI.objects.filter(tenant=tenant).first()
    )

    featured_products_form = FeaturedProductsUIForm(
        current_tenant=tenant,
        instance=FeaturedProductsUI.objects.filter(tenant=tenant).first(),
    )

    if request.method == "POST":
        footer_form = FooterUIForm(request.POST, instance=footer_form.instance)
        topbar_form = TopBarUIForm(request.POST, instance=topbar_form.instance)
        image_with_text_form = ImageWithTextUIForm(
            request.POST, request.FILES, instance=image_with_text_form.instance
        )
        featured_products_form = FeaturedProductsUIForm(
            request.POST, instance=featured_products_form.instance
        )

        for form in [
            footer_form,
            topbar_form,
            image_with_text_form,
            featured_products_form,
        ]:
            if form.is_valid():
                form.instance.tenant = tenant

        if image_with_text_form.is_valid():
            image = image_with_text_form.cleaned_data.get("overlay_image")
            if not image:
                image_with_text_form.add_error("overlay_image", "Image is required.")
            elif not image.name.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
                image_with_text_form.add_error(
                    "image",
                    "Unsupported image format. Please upload JPG, JPEG, PNG, or GIF.",
                )

        if all(
            form.is_valid()
            for form in [
                footer_form,
                topbar_form,
                image_with_text_form,
                featured_products_form,
            ]
        ):
            footer_form.save()
            topbar_form.save()
            image_with_text_form.save()
            featured_products_form.save()

            return redirect("pasal_dashboard_storefront_ui")

    context = {
        "BASE_URL": settings.BASE_URL,
        "tenant": tenant.subdomain,
        "footer_form": footer_form,
        "topbar_form": topbar_form,
        "image_with_text_form": image_with_text_form,
        "featured_products_form": featured_products_form,
        "product_exists": products_exists,
    }

    return render(
        request=request,
        template_name="dashboard/tenant_store_front_layout.html",
        context=context,
    )


@login_required_tenant
def pasal_ui_store_information(request):
    tenant_employee = get_object_or_404(Employees, user=request.user)
    tenant = tenant_employee.tenant
    existing_information = StoreInformation.objects.filter(tenant=tenant).first()

    if request.method == "POST":

        form = AddStoreInformation(
            request.POST, request.FILES, instance=existing_information
        )
        context = {"form": form, "tenant": tenant}

        if form.is_valid():
            information_form = form.save(commit=False)
            information_form.tenant = tenant
            information_form.save()
            return render(
                request=request,
                template_name="dashboard/tenant_store_information_layout.html",
                context=context,
            )

        else:
            messages.error(request=request, message=f"Error {form.errors}")
            context = {"form": form, "tenant": tenant}
            return render(
                request=request,
                template_name="dashboard/tenant_store_information_layout.html",
                context=context,
            )

    if existing_information:
        form = AddStoreInformation(instance=existing_information)
    else:
        form = AddStoreInformation()

    context = {"form": form, "tenant": tenant}
    return render(
        request=request,
        template_name="dashboard/tenant_store_information_layout.html",
        context=context,
    )


# using htmx
@login_required_tenant
def pasal_create_product_image(request):
    tenant = Employees.objects.get(user=request.user).tenant
    if request.method == "POST":
        form = CreateProductImage(request.POST, request.FILES or None)
        if form.is_valid():
            image = form.save(commit=False)
            image.tenant = tenant
            image.save()
            print("image saved")
            return HttpResponseClientRefresh()
        else:
            print(form.errors)
            messages.error(request=request, message="Form validation failed")
    else:
        form = CreateProductImage()

    context = {"product_image_form": form}
    return render(
        request=request,
        template_name="dashboard/partials/tenant_create_product_image.html",
        context=context,
    )


# using htmx
@login_required_tenant
def pasal_create_product_category(request):
    tenant = Employees.objects.get(user=request.user).tenant
    if request.method == "POST":
        form = CreateCategory(request.POST or None)
        if form.is_valid():
            category_form = form.save(commit=False)
            category_form.tenant = tenant
            category_form.save()
            return HttpResponseClientRefresh()
        else:
            messages.error(request=request, message="Form Validation Error")
            return HttpResponseClientRefresh()
    else:
        form = CreateCategory()

    context = {"category_form": form}
    return render(
        request=request,
        template_name="dashboard/partials/tenant_create_product_category.html",
        context=context,
    )


@login_required_tenant
def pasal_list_products(request, page=1):
    tenant = Employees.objects.get(user=request.user).tenant
    products = Products.objects.filter(tenant=tenant)

    items_per_page = 10
    paginator = Paginator(products, items_per_page)

    try:
        current_page = int(page)
    except ValueError:
        current_page = 1
    try:
        paginated_products = paginator.page(current_page)
    except EmptyPage:
        paginated_products = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        paginated_products = paginator.page(1)

    context = {
        "products": paginated_products,
    }
    return render(
        request=request,
        template_name="dashboard/products/tenant_list_products.html",
        context=context,
    )


@login_required_tenant
def pasal_create_product(request):
    tenant = Employees.objects.get(user=request.user).tenant

    form = CreateProductForm(current_tenant=tenant)
    product_image_form = CreateProductImage()
    product_category = CreateCategory()

    product_images = ProductImages.objects.filter(tenant=tenant)

    if request.method == "POST":
        form = CreateProductForm(request.POST, request.FILES)
        if form.is_valid():
            product_form = form.save(commit=False)
            product_form.tenant = tenant
            if product_form.price <= 0:
                messages.error(
                    request=request, message="Product Price cannot be 0 or less than 0 "
                )
                return HttpResponseClientRefresh()

            if product_form.discount < 0 or product_form.discount > 100:
                messages.error(
                    request=request,
                    message="Discount cannot be less than 0 or more than 100 ",
                )
                return HttpResponseClientRefresh()

            if product_form.stock_quantity <= 0:
                messages.error(
                    request=request, message="Stock Quantity cannot be less than 0 "
                )
                return HttpResponseClientRefresh()

            stripe.Product(name=product_form.name)

            product_form.save()
            form.save_m2m()

            messages.success(
                request=request,
                message=f"Product {product_form.name} Created Successfully",
            )
            return redirect(reverse_lazy("pasal_create_product"))
        else:
            context = {
                "product_images": product_images,
                "category_form": product_category,
                "form": form,
                "tenant": tenant,
                "product_image_form": product_image_form,
            }
            return render(
                request=request,
                template_name="dashboard/products/tenant_create_product.html",
                context=context,
            )

    context = {
        "product_images": product_images,
        "category_form": product_category,
        "form": form,
        "tenant": tenant,
        "product_image_form": product_image_form,
    }
    return render(
        request=request,
        template_name="dashboard/products/tenant_create_product.html",
        context=context,
    )


@login_required_tenant
def pasal_edit_product(request, slug):
    tenant = Employees.objects.get(user=request.user).tenant
    product = Products.objects.get(slug=slug)
    form = EditProduct(instance=product)  # Pass the product instance to the form
    product_image_form = CreateProductImage()
    prodcut_category = CreateCategory()

    if request.method == "POST":
        form = EditProduct(request.POST, instance=product)
        if form.is_valid():
            product_form = form.save(commit=False)
            product_form.tenant = tenant
            product.slug = slug
            if product_form.price <= 0:
                messages.error(
                    request=request, message="Product Price cannot be 0 or less than 0 "
                )
                return HttpResponseClientRefresh()
            if product_form.discount < 0 or product_form.discount > 100:
                messages.error(
                    request=request,
                    message="Discount cannot be less than 0 or more than 100 ",
                )
                return HttpResponseClientRefresh()
            if product_form.stock_quantity <= 0:
                messages.error(
                    request=request, message="Stock Quantity cannot be less than 0 "
                )
                return HttpResponseClientRefresh()

            product_form.save()
            form.save_m2m()
            messages.success(request=request, message="Edited Successfully")
            return HttpResponseRedirect(
                reverse_lazy("pasal_list_product", kwargs={"page": 1})
            )
        else:
            messages.error(request=request, message=f"Error {form.errors}")
            return render(
                request=request,
                template_name="dashboard/products/tenant_create_product.html",
                context={"form": form},
            )

    context = {
        "form": form,
        "product_image_form": product_image_form,
        "category_form": prodcut_category,
    }
    return render(
        request=request,
        template_name="dashboard/products/tenant_create_product.html",
        context=context,
    )


@login_required_tenant
def pasal_delete_product(request, slug):
    products = get_object_or_404(Products, slug=slug)
    if request.htmx:
        messages.success(request=request, message="Deleted successfully")
        products.delete()
        return HttpResponseClientRefresh()


# employees
@login_required_tenant
def pasal_list_employees(request):
    tenant = Employees.objects.get(user=request.user).tenant
    all_employees = Employees.objects.filter(tenant=tenant)

    context = {
        "all_employees": all_employees,
    }
    return render(
        request=request,
        template_name="dashboard/tenant_list_employees.html",
        context=context,
    )


@login_required_tenant
def pasal_create_employees(request):
    tenant = Employees.objects.get(user=request.user).tenant
    form = EmployeeRegisterForm()

    if request.htmx:
        form = EmployeeRegisterForm(request.POST)
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        if get_user_model().objects.filter(email=email).exists():

            messages.error(
                request=request, message="User with this email already exists"
            )
            return HttpResponseClientRefresh()

        if password != password_confirm:
            messages.error(request=request, message="The Two Passwords Don't Match")
            return HttpResponseClientRefresh()

        elif form.is_valid():
            user = CustomUser.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
            )

            employee = form.save(commit=False)  # Corrected this line
            employee.user = user
            employee.tenant = tenant
            employee.is_owner = False
            employee.save()
            messages.success(request=request, message="Created successfully")
            return HttpResponseClientRefresh()

        else:
            messages.error(
                request=request,
                message=f"Error: {form.errors}",
            )
            return HttpResponseClientRefresh()


@login_required_tenant
def pasal_edit_employee(request, employee_id):
    employee = get_object_or_404(Employees, pk=employee_id)
    if request.method == "POST":
        user_form = CustomUserEditForm(request.POST, instance=employee.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request=request, message="Updated successfully")
            return redirect("list-employees")
    else:
        user_form = CustomUserEditForm(instance=employee.user)
    return render(
        request, "dashboard/tenant_edit_employees.html", {"user_form": user_form}
    )


@login_required_tenant
def pasal_delete_employee(request, employee_id):
    employee = get_object_or_404(Employees, pk=employee_id)
    user = get_object_or_404(CustomUser, employee=employee)
    current_employee_is_owner = Employees.objects.get(user=request.user).is_owner

    if not current_employee_is_owner:
        messages.error(request=request, message="Permission Denied")
        return HttpResponseClientRefresh()

    try:

        employee.delete()
        user.delete()
        messages.success(request=request, message="Deleted Successfully")

    except Exception as e:
        messages.error(request=request, message=f"Error {e}")

    return HttpResponseClientRefresh()


@login_required_tenant
def pasal_settings(request):
    tenant = Employees.objects.get(user=request.user).tenant
    context = {}
    return render(
        request=request, template_name="dashboard/tenant_settings.html", context=context
    )


@login_required_tenant
def pasal_settings_stripe(request):
    employee = Employees.objects.get(user=request.user)
    if not employee.is_owner:
        messages.error("Permission Denied")
        return HttpResponseClientRefresh()

    if request.POST:
        pass


@login_required_tenant
def pasal_list_customers(request):
    tenant = Employees.objects.select_related("tenant").get(user=request.user).tenant
    customers = Customer.objects.select_related("tenant").filter(tenant=tenant)
    context = {"customers": customers}
    return render(
        request=request,
        template_name="dashboard/tenant_list_customers.html",
        context=context,
    )


@login_required_tenant
def pasal_detail_customers(request, customer_id):
    tenant = Employees.objects.select_related("tenant").get(user=request.user).tenant
    customer = Customer.objects.get(tenant=tenant, id=customer_id)
    context = {"customer": customer}
    return render(
        request=request,
        template_name="dashboard/tenant_detail_customer.html",
        context=context,
    )


# order status
@login_required_tenant
def pasal_orders(request):
    tenant = Employees.objects.select_related("tenant").get(user=request.user).tenant
    pass


@login_required_tenant
def pasal_update_order_status(request, order_id):
    if request.htmx:
        try:
            order_status = request.POST.get("order_status")
            order = Order.objects.get(id=order_id)
            order.status = order_status  # Assign order_status, not order
            order.save()
            messages.success(
                request=request, message="Order Status Updated Successfully"
            )

        except Exception as e:
            messages.error(request=request, message=f"Error occurred {e}")

        return HttpResponseClientRefresh()
    else:
        return PermissionError()
