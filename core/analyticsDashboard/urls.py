from django.urls import path
from . import views

urlpatterns = [
    path('productMarketing/analyticsDashboard',
         views.analyticsDashboard, name='analytics_dashboard'),
]
