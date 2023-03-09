from django.urls import path, re_path
from . import views

urlpatterns = [
    path(
        "createProductEntryPoint/",
        views.CreateProductEntryPoint.as_view(),
        name="create_product_entry_point",
    ),
    path(
        "createDummySalesName/",
        views.CreateDummySalesName.as_view(),
        name="create_dummy_sales_name",
    ),
    path(
        "createDummyProduct/",
        views.CreateDummyProduct.as_view(),
        name="create_dummy_product",
    ),
    path(
        "createDummyCustomer/",
        views.CreateDummyCustomer.as_view(),
        name="create_dummy_customer",
    ),
]
