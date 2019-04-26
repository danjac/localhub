from django import forms
from django.utils.translation import ugettext_lazy as _


from communikit.content.models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "description")
        labels = {
            "title": _("Title (Optional)"),
        }
