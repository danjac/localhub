from django import forms
from django.utils.translation import ugettext_lazy as _


from communikit.content.models import Post


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["url"].widget.attrs.update(
            {"placeholder": _("Add a full link here")}
        )

    def clean(self):
        cleaned_data = super().clean()
        description = cleaned_data.get("description")
        url = cleaned_data.get("url")
        if not any((description, url)):
            raise forms.ValidationError(
                _("Either description or URL must be provided")
            )
        return cleaned_data

    class Meta:
        model = Post
        fields = ("title", "url", "description")
        labels = {"title": _("Title (Optional)"), "url": _("Link")}
