import datetime

from haystack import indexes

from zihu_clone.news.models import News
from zihu_clone.articles.models import Article
from zihu_clone.qa.models import Question
from django.contrib.auth import get_user_model
from taggit.models import Tag


class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/articles_text.txt')

    def get_model(self):
        return Article

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(status="P", updated_at__lte=datetime.datetime.now())


class NewsIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/news_text.txt')

    def get_model(self):
        return News

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(reply=False, updated_at__lte=datetime.datetime.now())


class QuestionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/questions_text.txt')

    def get_model(self):
        return Question

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(updated_at__lte=datetime.datetime.now())


class UserIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/users_text.txt')

    def get_model(self):
        return get_user_model()

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(updated_at__lte=datetime.datetime.now())


class TagsIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/tags_text.txt')

    def get_model(self):
        return Tag

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
