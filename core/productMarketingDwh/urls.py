# Francisco Falise, copyright 01/10/2022

from django.urls import path
from . import views


urlpatterns = [
    # test
    path("productMarketing/KPI", views.showKPI, name="KPI"),
    # see projects
    path(
        "productMarketing/boupOverview", views.boupTable, name="project_overview_full"
    ),
    path(
        "productMarketing/boupOverviewData",
        views.boupTableView.as_view(),
        name="project_overview_full_data",
    ),
    path(
        "productMarketing/boupOverviewSlim",
        views.boupTableSlim,
        name="project_overview",
    ),
    # josn endpoint for boup data table
    path(
        "productMarketing/boupOverview/allData",
        views.boupTableAllData,
        name="boupTableAllData",
    ),
    path(
        "productMarketing/boupOverview/slimData",
        views.boupTableSlimData,
        name="boupTableSlimData",
    ),
    path(
        "productMarketing/boupOverview/slim_data",
        views.ProjectAPIView.as_view(),
        name="product_marketing_json",
    ),
]
