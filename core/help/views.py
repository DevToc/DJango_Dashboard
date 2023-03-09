from datetime import datetime

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# boup forecast


@login_required
def help(request):
    return render(request, "help/help.html")
