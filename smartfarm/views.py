from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Crop
import pandas as pd
import ssl
from django.http import HttpResponse


class CropListView(ListView):
    model = Crop
    template_name = 'crops/index.html'
    context_object_name = 'crops'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Crop.objects.filter(Q(common_name__icontains=query))
        return Crop.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class CropDetailView(DetailView):
    model = Crop
    template_name = 'crops/detail.html'
    context_object_name = 'crop'


def get_crop_data(request):
    """
    Fetch and save crop data from a remote GitHub CSV file to the database.
    """
    ssl._create_default_https_context = ssl._create_unverified_context

    url = 'https://raw.githubusercontent.com/PanupunJanin/SmartFarm/refs/heads/main/cleaned_crops.csv'
    df = pd.read_csv(url)

    for _, row in df.iterrows():
        Crop.objects.update_or_create(
            scientific_name=row['scientific_name'],
            defaults={
                'common_name': row['common_name'],
                'optimal_temperature_min': row['optimal_temperature_min'],
                'optimal_temperature_max': row['optimal_temperature_max'],
                'optimal_humidity_min': row['optimal_humidity_min'],
                'optimal_humidity_max': row['optimal_humidity_max'],
                'optimal_light_min': row['optimal_light_min'],
                'optimal_light_max': row['optimal_light_max'],
                'source': row['source'],
            }
        )

    return HttpResponse("Crop data imported successfully from GitHub!")

