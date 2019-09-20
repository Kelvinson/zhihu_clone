from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "zihu_clone.users"
    verbose_name = "Users"

    def ready(self):
        try:
            import zihu_clone.users.signals  # noqa F401
        except ImportError:
            pass
