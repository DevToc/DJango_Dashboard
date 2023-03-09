from django.urls import path

from core.users import views


urlpatterns = [
    path("redirect/", view=views.UserRedirectView.as_view(), name="user_redirect_view"),
    path("update/", view=views.UserUpdateView.as_view(), name="user_update_view"),
    path(
        "<str:username>/", view=views.UserDetailView.as_view(), name="user_detail_view"
    ),
]
