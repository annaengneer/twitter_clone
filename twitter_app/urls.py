from django.urls import path
from . import views

app_name = 'twitter_app'

urlpatterns = [
    path('', views.top, name='top'),
    path('signup/', views.SignupView.as_view(), name="signup"),
    path('form/', views.form_view, name="form")
]