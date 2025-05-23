from django.views.generic import ListView, DetailView
from django.views import View
from django.db.models import Q
from django.shortcuts import render, redirect
from .models import Crop
import pandas as pd
import ssl


class CropListView(ListView):
    model = Crop
    template_name = 'crops/index.html'
    context_object_name = 'crops'

    def get_queryset(self):
        query = self.request.GET.get('q')
        crops = Crop.objects.all()

        if query:
            crops = crops.filter(
                Q(common_name__icontains=query) | Q(scientific_name__icontains=query)
            )

        # Add computed field
        for crop in crops:
            crop.first_common_name = crop.common_name.split(',')[0].strip()
        return crops

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class CropDetailView(DetailView):
    model = Crop
    template_name = 'crops/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        crop = self.get_object()

        # Get input values from GET parameters
        temp = self.request.GET.get('temperature')
        humidity = self.request.GET.get('humidity')
        light = self.request.GET.get('light')
        wet = self.request.GET.get('wet') == 'true'

        if temp and humidity and light:
            temperature = float(temp)
            humidity = float(humidity)
            light = float(light)

            # Temperature score
            temp_range = crop.optimal_temperature_max - crop.optimal_temperature_min
            if temp_range > 0:
                temp_score = max(0, 1 - abs(temperature - ((crop.optimal_temperature_min + crop.optimal_temperature_max) / 2)) / (temp_range / 2))
            else:
                temp_score = 1 if temperature == crop.optimal_temperature_min else 0

            # Humidity score
            humidity_range = crop.optimal_humidity_max - crop.optimal_humidity_min
            if humidity_range > 0:
                humidity_score = max(0, 1 - abs(humidity - ((crop.optimal_humidity_min + crop.optimal_humidity_max) / 2)) / (humidity_range / 2))
            else:
                humidity_score = 1 if humidity == crop.optimal_humidity_min else 0

            # Light score
            if crop.optimal_light_min <= light <= crop.optimal_light_max:
                light_score = 1.0
            else:
                light_range = crop.optimal_light_max - crop.optimal_light_min
                if light < crop.optimal_light_min:
                    dist = crop.optimal_light_min - light
                else:
                    dist = light - crop.optimal_light_max
                light_score = max(0, 1 - dist / (light_range / 2)) if light_range > 0 else 0

            # Overall score (percentage)
            overall_score = round((temp_score + humidity_score + light_score) / 3 * 100, 2)

            context.update({
                'temperature': temperature,
                'humidity': humidity,
                'light': light,
                'wet': wet,
                'temp_score': round(temp_score * 100, 2),
                'humidity_score': round(humidity_score * 100, 2),
                'light_score': round(light_score * 100, 2),
                'overall_score': overall_score,
                'suggestions': {
                    'temp': {
                        'delta': temperature - (crop.optimal_temperature_min + crop.optimal_temperature_max) / 2,
                        'optimal': (crop.optimal_temperature_min + crop.optimal_temperature_max) / 2
                    },
                    'humidity': {
                        'delta': humidity - (crop.optimal_humidity_min + crop.optimal_humidity_max) / 2,
                        'optimal': (crop.optimal_humidity_min + crop.optimal_humidity_max) / 2
                    },
                    'light': {
                        'delta': light - (crop.optimal_light_min + crop.optimal_light_max) / 2,
                        'optimal': (crop.optimal_light_min + crop.optimal_light_max) / 2
                    }
                }
            })

        return context


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

    return redirect('smartfarm:crop_index')


class CropRecommendationView(View):
    template_name = 'crops/recommend.html'

    def get(self, request):
        temperature = request.GET.get('temperature')
        humidity = request.GET.get('humidity')
        light = request.GET.get('light')
        wet = request.GET.get('wet')

        is_wet = wet == "true"
        crops = Crop.objects.all()
        recommendations = []

        if temperature and humidity and light:
            temperature = float(temperature)
            humidity = float(humidity)
            light = float(light)

            for crop in crops:
                # Temperature score
                temp_range = crop.optimal_temperature_max - crop.optimal_temperature_min
                if temp_range > 0:
                    temp_score = max(0, 1 - abs(temperature - ((crop.optimal_temperature_min + crop.optimal_temperature_max) / 2)) / (temp_range / 2))
                else:
                    temp_score = 1 if temperature == crop.optimal_temperature_min else 0

                # Humidity score
                humidity_range = crop.optimal_humidity_max - crop.optimal_humidity_min
                if humidity_range > 0:
                    humidity_score = max(0, 1 - abs(humidity - ((crop.optimal_humidity_min + crop.optimal_humidity_max) / 2)) / (humidity_range / 2))
                else:
                    humidity_score = 1 if humidity == crop.optimal_humidity_min else 0

                # Light score: full 100 if within range
                if crop.optimal_light_min <= light <= crop.optimal_light_max:
                    light_score = 1.0
                else:
                    # Penalize based on distance from nearest bound
                    light_range = crop.optimal_light_max - crop.optimal_light_min
                    if light < crop.optimal_light_min:
                        dist = crop.optimal_light_min - light
                    else:
                        dist = light - crop.optimal_light_max
                    # Normalize based on range, but avoid division by zero
                    light_score = max(0, 1 - dist / (light_range / 2)) if light_range > 0 else 0

                # Final scores
                temp_percent = round(temp_score * 100, 2)
                humidity_percent = round(humidity_score * 100, 2)
                light_percent = round(light_score * 100, 2)
                overall_score = round((temp_score + humidity_score + light_score) / 3 * 100, 2)
                optimal_temp = (crop.optimal_temperature_min + crop.optimal_temperature_max) / 2
                optimal_humidity = (crop.optimal_humidity_min + crop.optimal_humidity_max) / 2
                optimal_light = (crop.optimal_light_min + crop.optimal_light_max) / 2
                first_common_name = crop.common_name.split(',')[0].strip()

                recommendations.append({
                    'crop': crop,
                    'first_common_name': first_common_name,
                    'overall_score': overall_score,
                    'temp_score': temp_percent,
                    'humidity_score': humidity_percent,
                    'light_score': light_percent,
                    'optimal_temp': optimal_temp,
                    'optimal_humidity': optimal_humidity,
                    'optimal_light': optimal_light,
                    'temp_delta': round(optimal_temp - temperature, 2),
                    'temp_delta_abs': round(abs(optimal_temp - temperature), 2),
                    'humidity_delta': round(optimal_humidity - humidity, 2),
                    'humidity_delta_abs': round(abs(optimal_humidity - humidity), 2),
                    'light_delta': round(optimal_light - light, 2),
                    'light_delta_abs': round(abs(optimal_light - light), 2),
                    'input_temp': temperature,
                    'input_humidity': humidity,
                    'input_light': light,
                })

            recommendations.sort(key=lambda x: x['overall_score'], reverse=True)

        context = {
            'recommendations': recommendations,
            'temperature': temperature,
            'humidity': humidity,
            'light': light,
            'wet': is_wet,
        }
        return render(request, self.template_name, context)

