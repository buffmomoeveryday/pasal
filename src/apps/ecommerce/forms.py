from typing import Any

from django import forms


class CustomerLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())


# forms.py
from django import forms
from .models import Customer


import re
from django import forms
from django.core.exceptions import ValidationError
from django.contrib import messages


class CustomerUpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "email", "mobile_number", "address"]

    def clean(self):
        cleaned_data = super().clean()
        mobile_number = cleaned_data.get("mobile_number")

        if mobile_number and not re.match(r"^\d{10}$", mobile_number):
            raise ValidationError("Mobile number should be a 10-digit number.")

        return cleaned_data
