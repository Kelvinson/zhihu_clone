from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
class User(AbstractUser):
    nickname = models.CharField(null=True, blank=True, max_length=255, verbose_name='nickname')
    job_title = models.CharField(max_length=50, null=True, blank=True, verbose_name='job_title')
    introduction = models.TextField(blank=True, null=True, verbose_name='brief_intro')
    picture = models.ImageField(upload_to='profile_pics/',null=True, blank=True, verbose_name='picture')
    location = models.CharField(max_length=50, null=True, blank=True, verbose_name='city')
    personal_url = models.URLField(max_length=555, blank=True, null=True, verbose_name='personal link')
    weibo = models.URLField(max_length=255, blank=True, null=True, verbose_name='weibo_link')
    zhihu = models.URLField(max_length=255, blank=True, null=True, verbose_name='zhihu_lin')
    github = models.URLField(max_length=255, blank=True, null=True, verbose_name='Github_link')
    linkedin = models.URLField(max_length=255, blank=True, null=True, verbose_name='LinkedIn_link')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='creation time')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='update time')

    class Meta:
        verbose_name = 'Users'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    def get_profile_name(self):
        if self.nickname:
            return self.nickname
        return self.username

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})
