from __future__ import unicode_literals
import uuid

from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.db import models

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class News(models.Model):
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL,
                             related_name='publisher', verbose_name='users')
    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE,
                               related_name='thread', verbose_name='self connection')
    content = models.TextField(verbose_name='content updates')
    liked = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked news', verbose_name='liked users')
    reply = models.BooleanField(default=False, verbose_name='reply or not')
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='creation time')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='update time')

    class Meta:
        verbose_name = 'Home page'
        verbose_name_plural = verbose_name
        ordering = ("-created_at",)

    def __str__(self):
        return self.content

    def save(self, *args, **kwargs):
        super(News, self).save(*args, **kwargs)

        if not self.reply:
            channel_layer = get_channel_layer()
            payload = {
                "type": "receive",
                "key": "additional_news",
                "actor_name": self.user.username
            }
            async_to_sync(channel_layer.group_send)('notifications', payload)

    def switch_like(self, user):
        if user in self.liked.all():
            self.liked.remove(user)
        else:
            self.liked.add(user)

    def get_parent(self):
        if self.parent:
            return self.parent
        else:
            return self

    def reply_this(self, user, text):
        parent = self.get_parent()
        News.objects.create(
            user=user,
            content=text,
            reply=True,
            parent=parent
        )
    def get_thread(self):

        parent = self.get_parent()
        return parent.thread.all()

    def comment_count(self):

        return self.get_thread().count()

    def count_likers(self):

        return self.liked.count()

    def get_likers(self):

        return self.liked.all()
