from django.urls import path
from . import views

app_name = 'twitter_app'

urlpatterns = [
    path('', views.top, name='top'),
    path('signup/', views.SignupView.as_view(), name="signup"),
    path('profile/<str:username>/', views.profile_view, name='profile_detail'),
    path('settings/profile', views.profile_edit, name='profile_edit'),
    path('post/<int:post_id>', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/like', views.post_like, name='post_like'),
    path('post/<int:post_id>/repost', views.post_repost, name='post_repost'),
    path('follow/<str:username>/', views.follow_user, name='follow'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow'),
    path('post/<int:post_id>/bookmark', views.bookmark, name='bookmark'),
    path('bookmarks/', views.bookmark_list, name='bookmark_list'),
]