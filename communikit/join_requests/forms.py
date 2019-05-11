from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from communikit.communities.models import Community
from communikit.join_requests.models import JoinRequest
from communikit.types import ContextDict


class JoinRequestForm(forms.ModelForm):
    class Meta:
        model = JoinRequest
        fields = ("email",)

    def __init__(
        self,
        community: Community,
        sender: settings.AUTH_USER_MODEL,
        *args,
        **kwargs
    ):
        self.community = community
        self.sender = sender

        super().__init__(*args, **kwargs)

        if self.sender:
            del self.fields["email"]

    def clean(self) -> ContextDict:
        data = super().clean()
        if self.sender:
            qs = JoinRequest.objects.filter(sender=self.sender)
        else:
            qs = JoinRequest.objects.filter(email__iexact=data["email"])

        if qs.exists():
            raise ValidationError(
                _("You have already sent a request. Be patient.")
            )
        return data

    def save(self, commit=True) -> JoinRequest:
        instance = super().save(commit=False)
        instance.sender = self.sender
        instance.community = self.community
        if commit:
            instance.save()
        return instance
