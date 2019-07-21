from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

User = get_user_model()


class UserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class UserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "avatar", "email_preferences", "bio")
        widgets = {"email_preferences": forms.CheckboxSelectMultiple}
