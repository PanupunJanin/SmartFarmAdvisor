from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("smartfarm/", include("smartfarm.urls")),
    path("admin/", admin.site.urls),
]