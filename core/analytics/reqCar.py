import pandas as pd
import pandasql as ps
from productMarketing.queryJobs.SQL_query import *

from .models import *
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required
from .req73 import *
from .req74 import *
from .req75 import *
from .req76 import *
from .req77 import *
from .req78 import *
from .req79 import *
from .req80 import *

class KPIDashboardCar(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get(self, request):
        print("get car getting KPI Dashboard1")

        ###
        total_df = restructure_whole()
        
        one_right = req73right(total_df)
        one_middle = req73middle(total_df)
        one_left = req73left(total_df)

        two_right = req74right(total_df)
        two_left = req74left(total_df)

        three_right = req75right(total_df)
        three_lefttop = req75lefttop(total_df)
        three_leftbottom = req75leftbottom(total_df)

        four_right = req76right(total_df)
        four_lefttop = req76lefttop(total_df)
        four_leftbottom = req76leftbottom(total_df)

        five_json = req77(total_df)

        today = datetime.date.today()
        year = today.strftime("%Y")
        six_json = req78(total_df,year)

        seven_json = req79(total_df,year)

        eight_json = req80(total_df,year)

        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        return JsonResponse({"first":{"req73_data_right": one_right, "req73_data_middle": one_middle,"req73_data_left": one_left},
                             "second":{"req74_data_right": two_right, "req74_data_left": two_left},
                             "third":{"req75_data_right": three_right, "req75_data_lefttop": three_lefttop, "req75_data_leftbottom":three_leftbottom},
                             "forth":{"req76_data_right": four_right, "req76_data_lefttop": four_lefttop, "req76_data_leftbottom":four_leftbottom},
                             "fifth":{"req77_data": five_json},
                             "sixth":{"req78_data": six_json},
                             "seventh":{"req79_data": seven_json},
                             "eightth":{"req80_data": eight_json} }, safe=True)