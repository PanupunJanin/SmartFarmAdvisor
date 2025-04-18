from django.contrib import admin
from django.urls import include, path
from . import views

app_name = 'smartfarm'

urlpatterns = [
    path('', views.CropListView.as_view(), name='crop_index'),
    path('crop/<int:pk>/', views.CropDetailView.as_view(), name='crop_detail'),
    path('import-crops/', views.get_crop_data, name='import_crops'),
    path('recommend/', views.CropRecommendationView.as_view(), name='recommend_crops'),
    path("admin/", admin.site.urls),
]