from django.urls import path

from apps.home.views import (
    pasal_home,
    pasal_register,
    pasal_tac,
    # dashboard
    pasal_dashboard_login,
    pasal_dashboard_logout,
    pasal_dashboard_sales,
    pasal_dashboard,
    # agg views
    pasal_dashboard_total_sales,
    pasal_dashboard_average_order_value,
    pasal_dashboard_top_customer,
    pasal_dashboard_top_selling_products,
    pasal_dashboard_total_customers,
    pasal_dashboard_total_orders,
    pasal_dashboard_transactions_list,
    pasal_dashboard_order,
    # ui
    pasal_ui_storefront_layout,
    pasal_ui_store_information,
    # products
    pasal_create_product,
    pasal_create_product_image,
    pasal_create_product_category,
    pasal_list_products,
    pasal_edit_product,
    pasal_delete_product,
    # employees
    pasal_list_employees,
    pasal_create_employees,
    pasal_edit_employee,
    pasal_delete_employee,
    # settings
    pasal_settings,
    # customers
    pasal_list_customers,
    pasal_detail_customers,
    # order
    pasal_update_order_status,
    # charts
    pasal_chart_sales_report,
    pasal_chart_category_sales_report,
)

urlpatterns = [
    path(
        "home/",
        pasal_home,
        name="pasal_home",
    ),
    path(
        "terms-and-conditions",
        pasal_tac,
        name="pasal_terms_and_conditions",
    ),
    path(
        "register/",
        pasal_register,
        name="pasal-register-tenant",
    ),
    path(
        "login/",
        pasal_dashboard_login,
        name="pasal-dashboard-login",
    ),
    path(
        "logout/",
        pasal_dashboard_logout,
        name="pasal-dashboard-logout",
    ),
    path(
        "dashboard/",
        pasal_dashboard,
        name="pasal-dashboard",
    ),
]

sales = [
    path(
        "dashboard/sales/",
        pasal_dashboard_sales,
        name="pasal-dashboard-sales",
    ),
]

products = [
    path(
        "dashboard/products/add/",
        pasal_create_product,
        name="pasal_create_product",
    ),
    path(
        "dashboard/products/list/<int:page>/",
        pasal_list_products,
        name="pasal_list_product",
    ),
    path(
        "dashboard/products/edit/<slug:slug>/",
        pasal_edit_product,
        name="pasal_edit_product",
    ),
    path(
        "dashboard/products/delete/<slug:slug>/",
        pasal_delete_product,
        name="pasal_delete_product",
    ),
    path(
        "dashboard/products/add/image/",
        pasal_create_product_image,
        name="pasal_create_product_image",
    ),
    path(
        "dashboard/products/add/category/",
        pasal_create_product_category,
        name="pasal_create_category",
    ),
]

ui = [
    path(
        "dashboard/ui/storefront/",
        pasal_ui_storefront_layout,
        name="pasal_dashboard_storefront_ui",
    ),
    path(
        "dashboard/ui/products/",
        pasal_ui_storefront_layout,
        name="pasal-dashboard-ui-product-page",
    ),
    path(
        "dashboard/storeinformation/",
        pasal_ui_store_information,
        name="pasal_store_information",
    ),
]

customers = [
    path(
        "dashboard/customers/list/",
        pasal_list_customers,
        name="pasal-list-customers",
    ),
    path(
        "dashboard/customers/<int:customer_id>/",
        pasal_detail_customers,
        name="pasal-detail-customers",
    ),
]

employees = [
    path(
        "dashboard/employees/list/",
        pasal_list_employees,
        name="list-employees",
    ),
    path(
        "employees/create/",
        pasal_create_employees,
        name="create-employees",
    ),
    path(
        "employees/<int:employee_id>/edit/",
        pasal_edit_employee,
        name="edit-employee",
    ),
    path(
        "dashboard/employees/<int:employee_id>/delete/",
        pasal_delete_employee,
        name="delete-employee",
    ),
]


order = [
    path(
        "dashboard/order/<int:order_id>/update/",
        pasal_update_order_status,
        name="update_order_status",
    ),
]


charts = [
    path(
        "dashboard/charts/sales-report/",
        pasal_chart_sales_report,
        name="pasal_charts_sales_report",
    ),
    path(
        "dashboard/charts/category-sales-report/",
        pasal_chart_category_sales_report,
        name="pasal_chart_category_sales_report",
    ),
]

agg = [
    path(
        "dashboard/agg/total-sales/",
        pasal_dashboard_total_sales,
        name="pasal_dashboard_total_sales",
    ),
    path(
        "dashboard/agg/average-order-value/",
        pasal_dashboard_average_order_value,
        name="pasal_dashboard_average_order_value",
    ),
    path(
        "dashboard/agg/total-customers/",
        pasal_dashboard_total_customers,
        name="pasal_dashboard_total_customers",
    ),
    path(
        "dashboard/agg/total-orders/",
        pasal_dashboard_total_orders,
        name="pasal_dashboard_total_orders",
    ),
    path(
        "dashboard/agg/top-customer/",
        pasal_dashboard_top_customer,
        name="pasal_dashboard_top_customer",
    ),
    path(
        "dashboard/agg/top-selling-product/",
        pasal_dashboard_top_selling_products,
        name="pasal_dashboard_top_selling_products",
    ),
]


tables = [
    path(
        "dashboard/table/transactions-list/",
        pasal_dashboard_transactions_list,
        name="pasal_dashboard_transactions_list",
    ),
    path(
        "table/order-list/",
        pasal_dashboard_order,
        name="pasal_dashboard_order",
    ),
]

settings = [
    path(
        "dashboard/settings/",
        pasal_settings,
        name="pasal_settings",
    ),
]

urlpatterns += ui
urlpatterns += products
urlpatterns += employees
urlpatterns += customers
urlpatterns += order
urlpatterns += charts
urlpatterns += agg
urlpatterns += tables
urlpatterns += settings
urlpatterns += sales
