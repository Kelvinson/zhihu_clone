#asgi.py only takes effect when deployed
import os
import sys
import django
from channels.routing import get_default_application


# application加入查找路径中
app_path = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir))
sys.path.append(os.path.join(app_path, 'zihu_clone'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
django.setup()
application = get_default_application()
