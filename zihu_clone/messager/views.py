from asgiref.sync import async_to_sync
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView
from django.template.loader import render_to_string

from channels.layers import get_channel_layer

from zihu_clone.messager.models import Message
from zihu_clone.helpers import ajax_required


class MessagesListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "messager/message_list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MessagesListView, self).get_context_data()
        context['users_list'] = get_user_model().objects.filter(is_active=True).exclude(
            username=self.request.user
        ).order_by('-last_login')[:10]
        last_conversation = Message.objects.get_most_recent_conversation(self.request.user)
        context['active'] = last_conversation.username
        return context

    def get_queryset(self):
        active_user = Message.objects.get_most_recent_conversation(self.request.user)
        return Message.objects.get_conversation(self.request.user, active_user)


class ConversationListView(MessagesListView):

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ConversationListView, self).get_context_data()
        context['active'] = self.kwargs["username"]
        return context

    def get_queryset(self):
        active_user = get_object_or_404(get_user_model(),
                                        username=self.kwargs["username"])
        return Message.objects.get_conversation(self.request.user, active_user)


@login_required
@ajax_required
@require_http_methods(["POST"])
def send_message(request):
    sender = request.user
    recipient_username = request.POST['to']
    recipient = get_user_model().objects.get(username=recipient_username)
    message = request.POST['message']
    if len(message.strip()) != 0 and sender != recipient:
        msg = Message.objects.create(
            sender=sender,
            recipient=recipient,
            message=message
        )

        channel_layer = get_channel_layer()
        payload = {
            'type': 'receive',
            'message': render_to_string('messager/single_message.html', {"message": msg}),
            'sender': sender.username
        }
        async_to_sync(channel_layer.group_send)(recipient.username, payload)
        return render(request, 'messager/single_message.html', {'message': msg})

    return HttpResponse()
