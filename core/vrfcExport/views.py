from datetime import datetime

from django.shortcuts import render
from django.db.models import Sum, F
from django.urls import reverse
from ajax_datatable.views import AjaxDatatableView

from productMarketingDwh.models import (
    BoUp,
    VrfcOrdersOnHand,
    VrfcSalesForecast,
    VrfcPmForecast,
)
from productMarketing.models import ProjectVolumeMonth
from core.project.models import Project
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.


# boup forecast
@login_required
def boup_forecast(request):
    return render(request, "vrfcExport/boupForecast.html")


@login_required
def vrfc_values(request):
    return render(request, "vrfcExport/boupVRFC.html")


@login_required
def vrfc_deepdive(request, mc_id, ec_id, rfp_id):
    current_year = datetime.now().year
    three_years_after = current_year + 3
    # queryset from project volume month sort by fiscal year and fiscal quarter
    project_vol_queryset = ProjectVolumeMonth.objects.filter(
        project__mainCustomer__id=mc_id,
        project__finalCustomer__id=ec_id,
        project__sales_name__rfp__id=rfp_id,
        calenderYear__gte=current_year,
        calenderYear__lte=three_years_after,
    ).order_by(
        "fiscal_year",
        "fiscal_quarter",
    )
    projects_ids = list(set(project_vol_queryset.values_list("project_id", flat=True)))
    projects = Project.objects.filter(id__in=projects_ids)
    # getting project id
    instance = project_vol_queryset.first()
    project_id = instance.project_id
    mc = instance.project.mainCustomer.customerName
    ec = instance.project.finalCustomer.finalCustomerName
    rfp = instance.project.sales_name.rfp
    obj_data = {
        "mc": mc,
        "ec": ec,
        "rfp": rfp,
        "project_id": project_id,
    }

    project_vol_aggr_list = project_vol_queryset.values(
        "fiscal_year",
        "fiscal_quarter",
    ).annotate(total_quantity=Sum("quantity"))

    orders_on_hand_queryset = VrfcOrdersOnHand.objects.filter(
        year__gte=current_year,
        year__lte=three_years_after,
        rfp_id=rfp_id,
        mainCustomerVrfc_id=mc_id,
        endCustomerVrfc_id=ec_id,
    )
    orders_on_hand_aggr_list = orders_on_hand_queryset.values(
        "fiscalYear", "fiscalQuarter"
    ).annotate(quantity=Sum("quantity"))
    order_delta_volume = []

    for volume, orders in zip(project_vol_aggr_list, orders_on_hand_aggr_list):
        order_delta_volume.append(
            {
                "fiscal_year": volume.get("fiscal_year", 0),
                "fiscal_quarter": volume.get("fiscal_quarter", 0),
                "quantity_diff": volume.get("total_quantity", 0)
                - orders.get("quantity", 0),
            }
        )

    sales_forecast_queryset = VrfcSalesForecast.objects.filter(
        year__gte=current_year,
        year__lte=three_years_after,
        rfp_id=rfp_id,
        mainCustomerVrfc_id=mc_id,
        endCustomerVrfc_id=ec_id,
    )
    sales_forecast_aggr_list = sales_forecast_queryset.values(
        "fiscalYear", "fiscalQuarter"
    ).annotate(quantity=Sum("quantity"))

    sales_forecast_delta_volume = []
    for volume, orders in zip(project_vol_aggr_list, sales_forecast_aggr_list):
        sales_forecast_delta_volume.append(
            {
                "fiscal_year": volume.get("fiscal_year", 0),
                "fiscal_quarter": volume.get("fiscal_quarter", 0),
                "quantity_diff": volume.get("total_quantity", 0)
                - orders.get("quantity", 0),
            }
        )
    pm_forecast_queryset = VrfcPmForecast.objects.filter(
        fiscalYear=current_year,
        quarter=three_years_after,
        rfp_id=rfp_id,
        mainCustomerVrfc_id=mc_id,
        endCustomerVrfc_id=ec_id,
    )
    pm_forecast_aggr_list = pm_forecast_queryset.values(
        "fiscalYear", "quarter"
    ).annotate(quantity=Sum("quantity"))

    pm_forecast_delta_volume = []
    for volume, orders in zip(project_vol_aggr_list, pm_forecast_aggr_list):
        pm_forecast_delta_volume.append(
            {
                "fiscal_year": volume.get("fiscal_year", 0),
                "fiscal_quarter": volume.get("fiscal_quarter", 0),
                "quantity_diff": volume.get("total_quantity", 0)
                - orders.get("quantity", 0),
            }
        )

    charts_data = {
        "project_vol_aggr_list": [
            item.get("total_quantity") for item in project_vol_aggr_list
        ],
        "orders_on_hand_aggr_list": [
            item.get("quantity") for item in orders_on_hand_aggr_list
        ],
        "sales_forecast_aggr_list": [
            item.get("quantity") for item in sales_forecast_aggr_list
        ],
    }

    return render(
        request,
        "vrfcExport/vrfcDeepDive.html",
        {
            "project_vol_aggr_list": project_vol_aggr_list,
            # orders on hand
            "orders_on_hand_aggr_list": orders_on_hand_aggr_list,
            "order_delta_volume": order_delta_volume,
            # sales forecast
            "sales_forecast_aggr_list": sales_forecast_aggr_list,
            "sales_forecast_delta_volume": sales_forecast_delta_volume,
            # pm forecast
            "pm_forecast_aggr_list": pm_forecast_aggr_list,
            "pm_forecast_delta_volume": pm_forecast_delta_volume,
            # prject details
            "obj_data": obj_data,
            "charts_data": charts_data,
            "projects": projects,
        },
    )


# def vrfc_deepdive(request, mc_id, ec_id, rfp_id):
#     current_year = datetime.now().year
#     three_years_after = current_year + 3

#     queryset = ProjectVolumeMonth.objects.filter(
#         project__mainCustomer__id=mc_id,
#         project__finalCustomer__id=ec_id,
#         project__sales_name__rfp__id=rfp_id,
#         calenderYear__gte=current_year,
#         calenderYear__lte=three_years_after,
#     )
#     # Get the data from the database
#     first_row = queryset.values("calenderYear", "month").annotate(
#         total_quantity=Sum("quantity")
#     )

#     # Create a list with the headers (quarter/fiscal year)
#     headers = []
#     for year in range(current_year, three_years_after + 1):
#         for quarter in range(1, 5):
#             headers.append(f"{year} FQ{quarter}")

#     # Create a dictionary with fiscal year-quarter keys and total quantity values
#     first_row_dict = {}
#     for row in first_row:
#         year = row["calenderYear"]
#         month = row["month"]
#         fiscal_year = year if month >= 7 else year - 1
#         quarter = (month - 1) // 3 + 1
#         key = f"{fiscal_year} FQ{quarter}"
#         value = row["total_quantity"]
#         first_row_dict[key] = value

#     # second row
#     second_row_dict = {}
#     for row in queryset:
#         year = row.calenderYear
#         month = row.month

#         fiscal_year = year if month >= 7 else year - 1
#         quarter = (month - 1) // 3 + 1
#         key = f"{fiscal_year} FQ{quarter}"
#         value = row.quantity
#         second_row_dict[key] = value
#     print(queryset)
#     return render(
#         request,
#         "vrfcExport/vrfcDeepDive.html",
#         {
#             "headers": headers,
#             "first_row_dict": first_row_dict,
#             "second_row_dict": second_row_dict,
#         },
#     )


class BOUP_ForecastAjax(AjaxDatatableView, LoginRequiredMixin):
    model = BoUp
    search_values_separator = "+"
    length_menu = [[10, 20, 50, 100], [10, 20, 50, 100]]
    disable_queryset_optimization = True
    column_defs = [
        {
            "name": "pk",
            "title": "Details",
            "searchable": False,
        },
        {
            "name": "mc_id",
            "title": "MC ID",
        },
        {"name": "ec_id", "title": "EC ID"},
        {"name": "rfp_id", "title": "RFP ID"},
        {
            "name": "mainCustomer",
            "title": "Main Customer",
            "foreign_field": "mainCustomer__customerName",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "endCustomer",
            "title": "End Customer",
            "foreign_field": "endCustomer__finalCustomerName",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "rfp",
            "title": "RFP",
            "foreign_field": "rfp__rfp",
        },
        {"name": "wVol2020", "title": "W Vol 2020"},
        {"name": "wVol2021", "title": "W Vol 2021"},
        {"name": "wVol2022", "title": "W Vol 2022"},
        {"name": "wVol2023", "title": "W Vol 2023"},
        {"name": "wVol2024", "title": "W Vol 2024"},
        {"name": "wVol2025", "title": "W Vol 2025"},
        {"name": "wVol2026", "title": "W Vol 2026"},
        {"name": "wVol2027", "title": "W Vol 2027"},
        {"name": "wVol2028", "title": "W Vol 2028"},
        {"name": "wVol2029", "title": "W Vol 2029"},
        {"name": "wVol2030", "title": "W Vol 2030"},
        {"name": "wVol2031", "title": "W Vol 2031"},
        {"name": "wVol2032", "title": "W Vol 2032"},
        {"name": "wVol2033", "title": "W Vol 2033"},
        {"name": "wVol2034", "title": "W Vol 2034"},
        {"name": "wVol2035", "title": "W Vol 2035"},
        {"name": "wVol2036", "title": "W Vol 2036"},
        {"name": "wVol2037", "title": "W Vol 2037"},
        {"name": "wVol2038", "title": "W Vol 2038"},
        {"name": "wVol2039", "title": "W Vol 2039"},
        {"name": "wVol2040", "title": "W Vol 2040"},
        {"name": "wVol2041", "title": "W Vol 2041"},
        {"name": "wVol2042", "title": "W Vol 2042"},
        {"name": "wVol2043", "title": "W Vol 2043"},
        {"name": "wVol2044", "title": "W Vol 2044"},
    ]

    def get_initial_queryset(self, request=None):
        queryset = super().get_initial_queryset()
        query = (
            queryset.select_related("mainCustomer", "endCustomer", "rfp")
            .group_by(
                "mainCustomer",
                "endCustomer",
                "rfp",
            )
            .annotate(
                mc_id=F("mainCustomer__id"),
                ec_id=F("endCustomer__id"),
                rfp_id=F("rfp__id"),
                wVol2020=Sum("wVol2020"),
                wVol2021=Sum("wVol2021"),
                wVol2022=Sum("wVol2022"),
                wVol2023=Sum("wVol2023"),
                wVol2024=Sum("wVol2024"),
                wVol2025=Sum("wVol2025"),
                wVol2026=Sum("wVol2026"),
                wVol2027=Sum("wVol2027"),
                wVol2028=Sum("wVol2028"),
                wVol2029=Sum("wVol2029"),
                wVol2030=Sum("wVol2030"),
                wVol2031=Sum("wVol2031"),
                wVol2032=Sum("wVol2032"),
                wVol2033=Sum("wVol2033"),
                wVol2034=Sum("wVol2034"),
                wVol2035=Sum("wVol2035"),
                wVol2036=Sum("wVol2036"),
                wVol2037=Sum("wVol2037"),
                wVol2038=Sum("wVol2038"),
                wVol2039=Sum("wVol2039"),
                wVol2040=Sum("wVol2040"),
                wVol2041=Sum("wVol2041"),
                wVol2042=Sum("wVol2042"),
                wVol2043=Sum("wVol2043"),
                wVol2044=Sum("wVol2044"),
            )
            .distinct()
        )

        return query

    def customize_row(self, row, obj):
        url = reverse(
            "vrfc_values_deepdive",
            kwargs={
                "mc_id": row["mc_id"],
                "ec_id": row["ec_id"],
                "rfp_id": row["rfp_id"],
            },
        )

        row[
            "pk"
        ] = f"""
        <div class="d-flex gap-2"><a href={url} class="btn btn-outline-success waves-effect waves-light"> View Details</a></div>
        """


class VRFC_ForecastAjax(AjaxDatatableView):
    model = VrfcOrdersOnHand
    search_values_separator = "+"
    length_menu = [[10, 20, 50, 100], [10, 20, 50, 100]]
    disable_queryset_optimization = True
    column_defs = [
        {
            "name": "mainCustomerVrfc",
            "title": "Main Customer",
            "foreign_field": "mainCustomerVrfc__customerName",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "endCustomerVrfc",
            "title": "End Customer",
            "foreign_field": "endCustomerVrfc__finalCustomerName",
            "choices": True,
            "autofilter": True,
        },
        {
            "name": "rfp",
            "title": "RFP",
            "foreign_field": "rfp__rfp",
        },
        {"name": "year", "title": "Year"},
        {"name": "quantity", "title": "Quantity"},
    ]

    def get_initial_queryset(self, request=None):
        queryset = super().get_initial_queryset()
        query = (
            queryset.select_related("mainCustomerVrfc", "endCustomerVrfc", "rfp")
            .group_by("mainCustomerVrfc", "endCustomerVrfc", "rfp", "year")
            .annotate(quantity=Sum("quantity"))
            .distinct()
        )
        return query
