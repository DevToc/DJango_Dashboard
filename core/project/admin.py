from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(
    (
        MainCustomers,
        FinalCustomers,
        ProductFamily,
        ProductSeries,
        ProductPackage,
        SalesName,
        ApplicationMain,
        ApplicationDetail,
        marketerMetadata,
        Project,
        ProjectError,
    )
)
