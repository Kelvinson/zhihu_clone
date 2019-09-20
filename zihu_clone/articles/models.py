from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.db import models
from django.db.models import Count

from slugify import slugify
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from taggit.managers import TaggableManager

class ArticleQuerySet(models.query.QuerySet):
    "self defined query set for convinience of reuse"

    def get_published(self):
        return self.filter(status="P").select_related('user')

    def get_drafts(self):
        return self.filter(status="D").select_related('user')

    def get_counted_tags(self):
        tag_dict = {}
        for obj in self.all():
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1

                else:
                    tag_dict[tag] += 1
        return tag_dict.items()



class Article(models.Model):
    STATUS = (("D", "Draft"), ("P", "Published"))

    title = models.CharField(max_length=255, null=False, unique=True, verbose_name='titles')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="author", on_delete=models.SET_NULL, verbose_name='author')
    image = models.ImageField(upload_to='articles_pictures/%Y/%m/%d/', verbose_name='article image')
    slug = models.SlugField(max_length=80, null=True, blank=True, verbose_name='(URL)alias')
    status = models.CharField(max_length=1, choices=STATUS, default='D', verbose_name='status(draft or published)')
    content = MarkdownxField(verbose_name='content')
    edited = models.BooleanField(default=False, verbose_name='editable')
    tags = TaggableManager(help_text='use comma(,) to seperate multiple tags', verbose_name='tags')
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='creation time')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='update time')
    objects = ArticleQuerySet.as_manager()

    class Meta:
        verbose_name = 'article'
        verbose_name_plural = verbose_name
        ordering = ("created_at",)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Article, self).save(*args, **kwargs)

    def get_markdown(self):
        "use markdown extension to markdownify the content"
        return markdownify(self.content)
