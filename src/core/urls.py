from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.ecommerce.views import store_front
from apps.home.views import pasal_home, pasal_register

urlpatterns = [
    path("", include("apps.home.urls"), name="pasal-home"),
    path("", include("apps.ecommerce.urls"), name="ecommerce"),
]
admin_url = [
    path("admin/", admin.site.urls),
]

urlpatterns += admin_url
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
