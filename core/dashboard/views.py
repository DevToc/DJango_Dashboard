from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from currencies.utils import (
    calculate,
    convert,
    get_active_currencies_qs,
    get_currency_code,
)

from core.project.models import ProjectError

# Create your views here.


class Dashboard(LoginRequiredMixin, View):
    template_name = "dashboard/dashboard.html"

    def get(self, request, *args, **kwargs):
        # add data here to render to the template
        errors = ProjectError.objects.select_related(
            "project",
            "project__applicationDetail",
            "project__applicationMain",
            "project__status",
            "project__secondRegion",
            "project__mainCustomer",
            "project__finalCustomer",
            "project__sales_name",
        )
        context = {"projectErrors": errors}
        return render(request, self.template_name, context)
