from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, DeleteView

from zihu_clone.helpers import ajax_required, AuthorRequiredMixin
from zihu_clone.news.models import News


class NewsListView(LoginRequiredMixin, ListView):
    model = News
    paginate_by = 20
    template_name = 'news/news_list.html'

    def get_queryset(self, **kwargs):
        return News.objects.filter(reply=False).select_related('user', 'parent').prefetch_related('liked')


class NewsDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = News
    template_name = 'news/news_confirm_delete.html'
    success_url = reverse_lazy("news:list")


@login_required
@ajax_required
@require_http_methods(['POST'])
def post_news(request):
    post = request.POST['post'].strip()
    if post:
        posted = News.objects.create(user=request.user, content=post)
        html = render_to_string('news/news_single.html', {'news': posted, 'request':request})
        return  HttpResponse(html)
    else:
        return HttpResponseBadRequest("content cannot be empty!")

@login_required
@ajax_required
@require_http_methods(["POST"])
def like(request):
    news_id = request.POST['news']
    news = News.objects.get(pk=news_id)
    news.switch_like(request.user)
    return JsonResponse({"likes": news.count_likers()})


@login_required
@ajax_required
@require_http_methods(["GET"])
def get_thread(request):
    news_id = request.GET['news']
    news = News.objects.select_related('user').get(pk=news_id)
    news_html = render_to_string("news/news_single.html", {"news": news})
    thread_html = render_to_string("news/news_thread.html", {"thread": news.get_thread()})
    return JsonResponse({
        "uuid": news_id,
        "news": news_html,
        "thread": thread_html,
    })


@login_required
@ajax_required
@require_http_methods(["POST"])
def post_comment(request):
    post = request.POST['reply'].strip()
    parent_id = request.POST['parent']
    parent = News.objects.get(pk=parent_id)
    if post:
        parent.reply_this(request.user, post)
        return JsonResponse({'comments': parent.comment_count()})
    else:
        return HttpResponseBadRequest("content cannot be empty!")


@login_required
@ajax_required
@require_http_methods(["POST"])
def update_interactions(request):
    data_point = request.POST['id_value']
    news = News.objects.get(pk=data_point)
    return JsonResponse({'likes': news.count_likers(), 'comments': news.comment_count()})

