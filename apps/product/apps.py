from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.product"  # full python path to this app package
    label = "product"  # app_label used in AUTH_USER_MODEL ('user.User')
