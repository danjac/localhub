from django import forms

from communikit.events.models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = (
            "title",
            "description",
            "url",
            "starts",
            "ends",
            "street_address",
            "locality",
            "postal_code",
            "region",
            "country",
        )
