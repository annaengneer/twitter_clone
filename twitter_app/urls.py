from django.urls import path
from . import views

app_name = 'twitter_app'

urlpatterns = [
    path('', views.top, name='top'),
    path('signup/', views.SignupView.as_view(), name="signup"),
    path('profile/<str:username>/', views.profile_view, name='profile_detail'),
    path('profile/',views.ProfileView, name="profile"),
    path('profile/edit/', views.edit_profile, name='profile_edit'),
]