import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from twitter_app.models import Post
from django.utils import timezone

User = get_user_model()

for i in range(10):
    user = User.objects.create_user(
        username=f'user{i}',
        email=f'user{i}@example.com',
        password='testpass123'
    )
    Post.objects.create(
        user=user,
        memo=f'これはテスト投稿{i}',
        created_at=timezone.now()
    )

