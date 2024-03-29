from __future__ import unicode_literals
import uuid
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.core import serializers

from slugify import slugify

class NotificationQuerySet(models.query.QuerySet):

    def unread(self):
        return self.filter(unread=True).select_related('actor', 'recipient')

    def read(self):
        return self.filter(unread=False).select_related('actor', 'recipient')

    def mark_all_as_read(self, recipient=None):
        qs = self.unread()
        if recipient:
            qs = qs.filter(recipient=recipient)
        return qs.update(unread=False)

    def mark_all_as_unread(self, recipient=None):
        qs = self.read()
        if recipient:
            qs = qs.filter(recipient=recipient)
        return qs.update(unread=True)

    def get_most_recent(self, recipient=None):
        qs = self.unread()[:5]
        if recipient:
            qs = qs.filter(recipient=recipient)[:5]
        return qs

    def serialize_latest_notifications(self, recipient=None):
        qs = self.get_most_recent(recipient)
        notification_dic = serializers.serialize('json', qs)
        return notification_dic

class Notification(models.Model):
    """参考：https://github.com/django-notifications/django-notifications"""
    NOTIFICATION_TYPE = (
        ('L', 'liked'),  # like
        ('C', 'commented'),  # comment
        ('F', 'favored'),  # favor
        ('A', 'answered'),  # answer
        ('W', 'accepted the answer'),  # accept
        ('R', 'replied'),  # reply
        ('I', 'logged in'),  # logged in
        ('O', 'logged out'),  # logged out
    )
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="notify_actor",
                              on_delete=models.CASCADE, verbose_name="actor")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=False,
                                  related_name="notifications", on_delete=models.CASCADE, verbose_name='recipient')
    unread = models.BooleanField(default=True, verbose_name='unread')
    slug = models.SlugField(max_length=80, null=True, blank=True, verbose_name='URL alias')
    verb = models.CharField(max_length=1, choices=NOTIFICATION_TYPE, verbose_name="notification category")
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='creation time')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='creation time')

    content_type = models.ForeignKey(ContentType, related_name='notify_action_object', null=True, blank=True,
                                     on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255, null=True, blank=True)
    action_object = GenericForeignKey()

    objects = NotificationQuerySet.as_manager()

    class Meta:
        verbose_name = "notifications"
        verbose_name_plural = verbose_name
        ordering = ("-created_at",)

    def __str__(self):
        if self.action_object:
            return f'{self.actor} {self.get_verb_display()} {self.action_object}'
        return f'{self.actor} {self.get_verb_display()}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.slug:
            self.slug = slugify(f'{self.recipient} {self.uuid_id} {self.verb}')
        super(Notification, self).save()

    def mark_as_read(self):
        if self.unread:
            self.unread = False
            self.save()

    def mark_as_unread(self):
        if not self.unread:
            self.unread = True
            self.save()
