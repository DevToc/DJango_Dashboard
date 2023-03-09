from django.urls import path
from . import views

urlpatterns = [
    # boup forecast
    path("help/", views.help, name="help"),
]
