from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from django_comments.signals import comment_was_posted

from zihu_clone.articles.models import Article
from zihu_clone.articles.forms import ArticleForm
from zihu_clone.helpers import AuthorRequiredMixin
from zihu_clone.notifications.views import notification_handler


class ArticlesListView(LoginRequiredMixin, ListView):
    "published articles"
    model = Article
    paginate_by = 20
    context_object_name = "articles"
    template_name = "articles/article_list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ArticlesListView, self).get_context_data(*args, **kwargs)
        context['popular_tags'] = Article.objects.get_counted_tags()
        return context

    def get_queryset(self, **kwargs):
        return Article.objects.get_published()


class DraftsListView(ArticlesListView):
    def get_queryset(self, **kwargs):
        return Article.objects.filter(user=self.request.user).get_drafts()


@method_decorator(cache_page(60 * 60), name='get')
class CreateArticleView(LoginRequiredMixin, CreateView):
    model = Article
    message = "you have created an article successfully！"
    form_class = ArticleForm
    template_name = 'articles/article_create.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(CreateArticleView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse('articles:list')


class DetailArticleView(LoginRequiredMixin, DetailView):
    model = Article
    template_name = 'articles/article_detail.html'

    def get_queryset(self):
        return Article.objects.select_related('user').filter(slug=self.kwargs['slug'])


class EditArticleView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):  #take care the inheritance precedence in Python3
    """edit article"""
    model = Article
    message = "you have updated your article successfully！"
    form_class = ArticleForm
    template_name = 'articles/article_update.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(EditArticleView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse('articles:list')


def notify_comment(**kwargs):
    "notify authors when articles are commented"
    actor = kwargs['request'].user
    obj = kwargs['comment'].content_object

    notification_handler(actor, obj.user, 'C', obj)


comment_was_posted.connect(receiver=notify_comment)
