from django.apps import AppConfig


class TwitterAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'twitter_app'

    def ready(self):
        import twitter_app.signals