import os
import django
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from twitter_app.models import Post, Profile, Relation, Notification, Comment

User = get_user_model()

target_username = "annaengineer"
target_user = User.objects.filter(username=target_username).first()

if not target_user:
    print(f"ユーザー{target_username}が存在しません。")
    exit()
print(f"ユーザー {target_username} を取得しました。")

Profile.objects.get_or_create(user=target_user)

post = Post.objects.filter(user=target_user).first()

if not post:
    post = Post.objects.create(
        user=target_user,
        content=f"これは{target_username}の初投稿です！",
        created_at=timezone.now(),
    )
    print(f"{target_username} の投稿を作成しました。")
else:
    print(f"{target_username} の投稿は既に存在します。")

users = []

for i in range(10):
    username = f'user{i}'
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": f"{username}@example.com"}
    )
    
    if created:
        user.set_password("testpass123")
        user.save()
    users.append(user)

    Profile.objects.get_or_create(user=user)

    Post.objects.get_or_create(
        user=user,
        defaults={
        "content": f"これはテスト投稿{i}",
        "created_at": timezone.now()
    })
print("ユーザーと投稿の作成が完了しました。")

if post:
    for u in users:
        if u == target_user:
            continue
            
        Relation.objects.get_or_create(followers=u, followings=target_user)
        Notification.objects.get_or_create(
            to_user=target_user,
            from_user=u,
            notification_type=Notification.FOLLOW
        )
        
        Notification.objects.get_or_create(
            to_user=target_user,
            from_user=u,
            post=post,
            notification_type=Notification.LIKE
        )

        comment = Comment.objects.create(
            user=u,
            post=post,
            content=f"{u.username}からのテストコメントです！"
        )

        Notification.objects.create(
            to_user=target_user,
            from_user=u,
            post=post,
            comment=comment,
            notification_type=Notification.COMMENT
        )
    print("seedデータの作成が完了されました")