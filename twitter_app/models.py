from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
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
        regex=r'^[a-zA-Z0-9]+$',
        message="ユーザー名は英数字のみで構成してください"
    )

    username = models.CharField(max_length=20,unique=True,validators=[username_validator],blank=False)
    email = models.EmailField(unique=True,blank=False)
    birth_date = models.DateField(verbose_name=_("birth_date"),blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIlD = 'email'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name ="User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]