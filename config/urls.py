from django.contrib import admin
from django.urls import path,include
from twitter_app.views import top

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include("allauth.urls")),
    path('', include('twitter_app.urls')),
    path("", top, name="home"),
]
