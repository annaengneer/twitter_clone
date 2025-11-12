import os
import django
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from twitter_app.models import Post, Profile

User = get_user_model()

target_username = "@annaengineer"
target_user = User.objects.filter(username=target_username).first()

if target_user:
    profile, _ = Profile.objects.get_or_create(user=target_user)
    if not Post.objects.filter(user=target_user).exists():
        Post.objects.create(
            user=target_user,
            content=f"これは {target_username} の初投稿です！",
            created_at=timezone.now(),
        )
        print(f"{target_username} の投稿を作成しました。")
    else:
        print(f"{target_username} の投稿は既に存在します。")
else:
    print(f"ユーザー {target_username} が存在しません。")

for i in range(10):
    username = f'user{i}'
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": f"{username}@example.com",
            "password": "testpass123"
        }
    )

    if created:
        print(f"ユーザー {username} を作成しました。")
    else:
        print(f"ユーザー {username} は既に存在します。")

    profile, p_created = Profile.objects.get_or_create(user=user)
    if p_created:
        print(f"{username}のプロフィールを作成しました。")

    if not Post.objects.filter(user=user).exists():
        Post.objects.create(
            user=user,
            content=f"これはテスト投稿{i}",
            created_at=timezone.now()
        )
        print(f"user{i} の投稿を作成しました。")
    else:
        print(f"user{i} の投稿は既に存在します。")

print("seedデータの作成が完了しました。")