from django.db import models


class Crop(models.Model):
    scientific_name = models.CharField(max_length=100, blank=True, null=True)
    common_name = models.CharField(max_length=1000, unique=True)
    optimal_temperature_min = models.FloatField()
    optimal_temperature_max = models.FloatField()
    optimal_humidity_min = models.FloatField()
    optimal_humidity_max = models.FloatField()
    optimal_light_min = models.FloatField()
    optimal_light_max = models.FloatField()
    source = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.scientific_name


class Sensor(models.Model):
    SENSOR_TYPES = [
        ('soil', 'Soil Moisture'),
        ('light', 'Light Intensity'),
        ('temp', 'Temperature'),
        ('humidity', 'Humidity'),
    ]
    name = models.CharField(max_length=100)
    sensor_type = models.CharField(max_length=10, choices=SENSOR_TYPES)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_sensor_type_display()} - {self.name}"


class SensorData(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.sensor.name} - {self.timestamp}: {self.value}"


class CropSuitabilityResult(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_suitable = models.BooleanField()
    message = models.TextField()  # e.g., "Temperature too low", "Humidity within range"
    score = models.FloatField()   # Optional: a numeric score out of 100 for suitability

    def __str__(self):
        return f"{self.crop.name} - {self.timestamp} - {'Suitable' if self.is_suitable else 'Not Suitable'}"
