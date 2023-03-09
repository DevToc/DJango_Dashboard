from .models import *
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


@login_required(login_url="/login/")
def analyticsDashboard(request):

    # return render(request, 'analytics/businessInsights.html', {'product_list': product_list, 'step': 1, })
    return render(request, 'analytics/productMasterData.html', {'step': 1, })
