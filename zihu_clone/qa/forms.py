#!/usr/bin/python3



from django import forms
from markdownx.fields import MarkdownxFormField

from zihu_clone.qa.models import Question


class QuestionForm(forms.ModelForm):
    status = forms.CharField(widget=forms.HiddenInput())
    content = MarkdownxFormField()

    class Meta:
        model = Question
        fields = ["title", "content", "tags", "status"]
