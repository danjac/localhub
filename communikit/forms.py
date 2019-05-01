from django import forms
from django.utils.translation import ugettext_lazy as _

from communikit.comments.models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content",)
        labels = {"content": _("Comment")}
