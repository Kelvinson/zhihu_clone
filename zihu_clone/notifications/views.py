
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from zihu_clone.notifications.models import Notification
class NotificationUnreadListView(LoginRequiredMixin, ListView):
    model = Notification
    context_object_name = 'notification_list'
    template_name = 'notifications/notification_list.html'

    def get_queryset(self, **kwargs):
        return self.request.user.notifications.unread()


@login_required
def mark_all_as_read(request):
    request.user.notifications.mark_all_as_read()
    redirect_url = request.GET.get('next')

    messages.add_message(request, messages.SUCCESS, f'用户{request.user.username}的所有通知标为已读')

    if redirect_url:
        return redirect(redirect_url)

    return redirect('notifications:unread')


@login_required
def mark_as_read(request, slug):
    notification = get_object_or_404(Notification, slug=slug)
    notification.mark_as_read()

    redirect_url = request.GET.get('next')

    messages.add_message(request, messages.SUCCESS, f'mark {notification} as read')

    if redirect_url:
        return redirect(redirect_url)

    return redirect('notifications:unread')


@login_required
def get_latest_notifications(request):
    notifications = request.user.notifications.get_most_recent()
    return render(request, 'notifications/most_recent.html',
                  {'notifications': notifications})


def notification_handler(actor, recipient, verb, action_object, **kwargs):
    if actor.username != recipient.username and recipient.username == action_object.user.username:
        key = kwargs.get('key', 'notification')
        id_value = kwargs.get('id_value', None)
        Notification.objects.create(
            actor=actor,
            recipient=recipient,
            verb=verb,
            action_object=action_object
        )

        channel_layer = get_channel_layer()
        payload = {
            'type': 'receive',
            'key': key,
            'actor_name': actor.username,
            'id_value': id_value
        }
        async_to_sync(channel_layer.group_send)('notifications', payload)
