from django import forms
from django.contrib.auth.models import User
from unfold.forms import UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(render_value=True)
    )
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput(render_value=True)
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
