from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User,Profile,Post

# Register your models here.

class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('username', 'email', "display_name", 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("email", "display_name", "birth_date", "phone_number")}),
        ("Permissions", {"fields": ("is_active", "is_staff", 
        "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "display_name", 
            "password1", "password2", "is_staff", "is_active"),
        }),
    )

admin.site.register(User, UserAdmin)

class ProfileAdmin(admin.ModelAdmin):
    model = Profile
    list_display = ("get_username", "get_display_name" , "show_icon_image",
     "show_header_image", "introduce_content", "place", "website", "birth_date")

    fieldsets = (
       (None, {
           "fields": ("user" , "icon_image", "header_image",
                        "introduce_content", "place", "website", "birth_date")
        }),
    )

    def get_username(self, obj):
        return getattr(obj.user, "username", "不明ユーザー")
    get_username.short_description = "ユーザー名"

    def get_display_name(self, obj):
        return getattr(obj.user, "display_name", "不明ユーザー")
    get_display_name.short_description = "表示名"

    def show_icon_image(self, obj):
        """CloudinaryFieldを安全に文字列化し、存在すれば画像を表示"""
        if obj.icon_image and getattr(obj.icon_image, "url", None):
            return format_html('<img src="{}" width="50" height="50" />', obj.icon_image.url)
        return "（なし）"
    show_icon_image.short_description = "アイコン画像"

    def show_header_image(self, obj):
        """CloudinaryFieldを安全に文字列化し、存在すれば画像を表示"""
        if obj.header_image and getattr(obj.header_image, "url", None):
            return format_html('<img src="{}" width="100" />', obj.header_image.url)
        return "（なし）"
    show_header_image.short_description = "ヘッダー画像"

admin.site.register(Profile, ProfileAdmin)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "content", "created_at")
    list_filter = ("user", "created_at")
    search_fields = ("content", "user__username")
    ordering = ("-id",)