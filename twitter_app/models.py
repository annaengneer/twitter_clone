from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models
from cloudinary.models import CloudinaryField

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self,username,email,password, **extra_fields):

        if not username:
            raise ValueError('UserIDを入力してください')
        
        if not email:
            raise ValueError('メールアドレスを入力してください')
        
        if not password:
            raise ValueError('パスワードを入力してください')
        
        email = self.normalize_email(email)

        user = self.model(
            username = username,
            email = email,

            **extra_fields
        )

        user.set_password(password)

        user.save(using=self._db)
        return user
   
    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(username,email,password,**extra_fields)

phone_validtor = RegexValidator(
    regex=r'^[a-zA-Z0-9]+$',
    message="ユーザー名は英数字のみで構成してください"
)


class User(AbstractBaseUser,PermissionsMixin):
    
    username_validator = RegexValidator(
        regex=r'^[\w]+$',
        message="ユーザー名は英数字・アンダースコアのみ使えます"
    )

    username = models.CharField(max_length=20,unique=True,validators=[username_validator],blank=False)
    display_name = models.CharField(max_length=30, verbose_name="表示名")
    email = models.EmailField(unique=True,blank=False)
    birth_date = models.DateField(verbose_name=_("birth_date"),blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    objects = UserManager()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name ="User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]

class Relation(models.Model):
    followers = models.ForeignKey(User, related_name='follower', on_delete=models.CASCADE)
    followings = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        follower_name = getattr(self.followers, "username", None)
        following_name = getattr(self.followings, "username", None)
        follower_name = str(follower_name or "不明ユーザー")
        following_name = str(following_name or "不明ユーザー")
        return f"{follower_name} → {following_name}"

class Post(models.Model):
    content = models.TextField(default="")
    image = CloudinaryField('images', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    repost_from = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='reposts')
    
    @property
    def is_repost_post(self):
        return self.repost_from is not None

    def __str__(self):
        return f'{self.user.username} - {self.content[:20]}'

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=140)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"

User = get_user_model()
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user} -> {self.post}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    icon_image = CloudinaryField("images",null=True, blank=True)
    header_image = CloudinaryField("images",null=True, blank=True)
    introduce_content = models.TextField(default="")
    place = models.CharField(max_length=20,null=True, blank=False)
    website = models.URLField(max_length=200, blank=True, null=True)
    birth_date = models.DateField(verbose_name=_("birth_date"),blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def username(self):
        return self.user.username
    
    @property
    def display_name(self):
        return self.user.display_name
    
    @property
    def following_count(self):
        return Relation.objects.filter(followers=self.user).count()
    
    @property
    def follower_count(self):
        return Relation.objects.filter(followings=self.user).count()

    def __str__(self):
        username = str(getattr(self.user, "username", "不明ユーザー") or "不明ユーザー")
        display_name = str(getattr(self.user, "display_name", "") or "")
        return f"{display_name}{username}のプロフィール"

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarked')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} -> {self.post.id}"