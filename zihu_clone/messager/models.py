from __future__ import unicode_literals
import uuid

from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

class MessageQuerySet(models.query.QuerySet):

    def get_conversation(self, sender, recipient):
        """private messges between users"""
        qs_one = self.filter(sender=sender, recipient=recipient).select_related('sender', 'recipient')  # A->B
        qs_two = self.filter(sender=recipient, recipient=sender).select_related('sender', 'recipient')  # B->A
        return qs_one.union(qs_two).order_by('created_at')  # order by time

    def get_most_recent_conversation(self, recipient):
        try:
            qs_sent = self.filter(sender=recipient).select_related('sender', 'recipient')
            qs_received = self.filter(recipient=recipient).select_related('sender', 'recipient')
            qs = qs_sent.union(qs_received).latest("created_at")
            if qs.sender == recipient:
                return qs.recipient
            return qs.sender
        except self.model.DoesNotExist:
            return get_user_model().objects.get(username=recipient.username)

class Message(models.Model):
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages',
                               blank=True, null=True, on_delete=models.SET_NULL, verbose_name='sender')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages',
                                  blank=True, null=True, on_delete=models.SET_NULL, verbose_name='receiver')
    message = models.TextField(blank=True, null=True, verbose_name='message content')
    unread = models.BooleanField(default=True, verbose_name='read or unread')

    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='creation time')

    objects = MessageQuerySet.as_manager()

    class Meta:
        verbose_name = 'private messages'
        verbose_name_plural = verbose_name
        ordering = ('-created_at',)

    def __str__(self):
        return self.message

    def mark_as_read(self):
        if self.unread:
            self.unread = False
            self.save()
