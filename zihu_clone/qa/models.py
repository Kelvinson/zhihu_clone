from __future__ import unicode_literals
import uuid
from collections import Counter
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.db import models

from slugify import slugify
from markdownx.models import MarkdownxField
from taggit.managers import TaggableManager
from markdownx.utils import markdownify


class Vote(models.Model):
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='qa_vote',
                             on_delete=models.CASCADE, verbose_name='users')
    value = models.BooleanField(default=True, verbose_name='vote or against')
    """use CotentType to relate user's vote on the questions an answers"""
    content_type = models.ForeignKey(ContentType, related_name='votes_on', on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    vote = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='creation time')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='update time')

    class Meta:
        verbose_name = 'Vote'
        verbose_name_plural = verbose_name
        unique_together = ('user', 'content_type', 'object_id')
        #SQL optimization
        index_together = ('content_type', 'object_id')

class QuestionQuerySet(models.query.QuerySet):
    def get_answered(self):
        return self.filter(has_answer=True).select_related('user')

    def get_unanswered(self):
        return self.filter(has_answer=False).select_related('user')

    def get_counted_tags(self):
        tag_dict = {}
        for obj in self.all():
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1

                else:
                    tag_dict[tag] += 1
        return tag_dict.items()

class Question(models.Model):
    STATUS = (("O", "Open"), ("C", "Close"), ("D", "Draft"))

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="q_author",
                             on_delete=models.CASCADE, verbose_name='questioner')
    title = models.CharField(max_length=255, unique=True, verbose_name='title')
    slug = models.SlugField(max_length=80, null=True, blank=True, verbose_name='(URL)alias')
    status = models.CharField(max_length=1, choices=STATUS, default='O',
                              verbose_name='question status')
    content = MarkdownxField(verbose_name='content')
    tags = TaggableManager(help_text='use comma(,) to seperate multiple tags', verbose_name='tags')
    has_answer = models.BooleanField(default=False, verbose_name="accepted answer")
    votes = GenericRelation(Vote, verbose_name='vote result')
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='creation time')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='update time')

    objects = QuestionQuerySet.as_manager()

    class Meta:
        verbose_name = 'questions'
        verbose_name_plural = verbose_name
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Question, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_markdown(self):
        return markdownify(self.content)

    def total_votes(self):
        dic = Counter(self.votes.values_list('value', flat=True))
        return dic[True] - dic[False]

    def get_answers(self):
        return Answer.objects.filter(question=self).select_related('user', 'question')

    def count_answers(self):
        return self.get_answers().count()

    def get_upvoters(self):
        return [vote.user for vote in self.votes.filter(value=True).select_related('user').prefecth_related('vote')]

    def get_downvoters(self):
        return [vote.user for vote in self.votes.filter(value=False).select_related('user').prefecth_related('vote')]

class Answer(models.Model):
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='a_author', on_delete=models.CASCADE,
                             verbose_name='answer')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='questions')
    content = MarkdownxField(verbose_name='content')
    is_answer = models.BooleanField(default=False, verbose_name='whether the answer is accepted')
    votes = GenericRelation(Vote, verbose_name='vote result')
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='creation time')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='update time')

    class Meta:
        ordering = ('-is_answer', '-created_at')
        verbose_name = 'Answer'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content

    def get_markdown(self):
        return markdownify(self.content)

    def total_votes(self):
        dic = Counter(self.votes.values_list('value', flat=True))
        return dic[True] - dic[False]

    def get_upvoters(self):
        return [vote.user for vote in self.votes.filter(value=True).select_related('user').prefecth_related('vote')]

    def get_downvoters(self):
        return [vote.user for vote in self.votes.filter(value=False).select_related('user').prefecth_related('vote')]

    def accept_answer(self):
        answer_set = Answer.objects.filter(question=self.question)
        answer_set.update(is_answer=False)
        self.is_answer = True
        self.save()
        self.question.has_answer = True
        self.question.save()