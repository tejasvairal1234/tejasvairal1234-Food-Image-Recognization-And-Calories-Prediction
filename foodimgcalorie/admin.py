from django.contrib import admin
from .models import User, FoodPrediction

# Register your models here.
admin.site.register(User)
admin.site.register(FoodPrediction)
