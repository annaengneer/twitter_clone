from django.urls import path
from . import views

app_name = 'twiiter_app'

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path('signup/', views.SignupView.as_view(), name="signup"),
]