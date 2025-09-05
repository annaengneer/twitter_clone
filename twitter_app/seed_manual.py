from django.contrib.auth import get_user_model
from twitter_app.models import Post
from django.utils import timezone
import random

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
        create_at=timezone.now()
    )

