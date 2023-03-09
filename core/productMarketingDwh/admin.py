from django.contrib import admin
from .models import BoUp, VrfcOrdersOnHand, VrfcSalesForecast

admin.site.register((BoUp, VrfcOrdersOnHand, VrfcSalesForecast))
