from django import forms
from django.contrib.auth.models import User


class UserRegisterForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    repassword = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cd = super().clean()
        password = cd.get('password')
        repassword = cd.get('repassword')
        if password and repassword and password != repassword:
            raise forms.ValidationError('password and repassword not match!')
        return cd


class UserLoginForm(forms.Form):
    username_email  = forms.CharField()
    password = forms.CharField()

