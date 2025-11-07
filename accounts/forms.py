# accounts/forms.py
from django import forms

class SpecialCodeForm(forms.Form):
    code = forms.CharField(max_length=32, label="Company Code")

class AdminLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
