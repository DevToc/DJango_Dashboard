from django.urls import path
from . import views

urlpatterns = [
    # boup forecast
    path("productMarketing/boup-forecast/", views.boup_forecast, name="boup_forecast"),
    path("productMarketing/vrfc-values/", views.vrfc_values, name="vrfc_values"),
    path(
        "productMarketing/vrfc-values/<str:mc_id>/<str:ec_id>/<str:rfp_id>/",
        views.vrfc_deepdive,
        name="vrfc_values_deepdive",
    ),
    path(
        "productMarketing/boup-forecast/ajax/",
        views.BOUP_ForecastAjax.as_view(),
        name="boup_forecast_ajax",
    ),
    path(
        "productMarketing/vrfc-values/ajax/",
        views.VRFC_ForecastAjax.as_view(),
        name="vrfc_values_ajax",
    ),
]
