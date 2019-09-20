from django.urls import path
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from zihu_clone.messager.consumers import MessagesConsumer
from zihu_clone.notifications.consumers import NotificationsConsumer


application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                path('ws/notifications/', NotificationsConsumer),
                path('ws/<str:username>/', MessagesConsumer),
            ])
        )
    )
})

