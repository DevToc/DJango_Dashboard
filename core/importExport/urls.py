from django.urls import path, re_path
from . import views

urlpatterns = [
    path(
        "importExport/",
        views.importExport.as_view(),
        name="import_export_main",
    ),
    path('importExport/download/<str:filename>/', views.download_file)
]
