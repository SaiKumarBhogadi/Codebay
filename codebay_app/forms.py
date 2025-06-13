from django import forms

class ContactForm(forms.Form):
    full_name = forms.CharField(max_length=100, required=True, label="Full Name")
    email = forms.EmailField(required=True, label="Email Address")
    phone = forms.CharField(max_length=20, required=False, label="Phone Number")
    company = forms.CharField(max_length=100, required=False, label="Company/Organization")
    website_type = forms.ChoiceField(
        choices=[
            ("business", "Business Website"),
            ("ecommerce", "E-commerce Store"),
            ("blog", "Blog"),
            ("portfolio", "Portfolio"),
            ("landing", "Landing Page"),
            ("other", "Other"),
        ],
        required=True,
        label="Website Type",
        widget=forms.RadioSelect,
    )
    budget = forms.ChoiceField(
        choices=[
            ("under-500", "$0 - $500"),
            ("500-1000", "$500 - $1,000"),
            ("1000-5000", "$1,000 - $5,000"),
            ("5000-plus", "$5,000+"),
        ],
        required=True,
        label="Budget Range",
    )
    timeline = forms.ChoiceField(
        choices=[
            ("1-month", "Within 1 Month"),
            ("1-3-months", "1-3 Months"),
            ("3-6-months", "3-6 Months"),
            ("6-plus", "6+ Months"),
        ],
        required=False,
        label="Project Timeline",
    )
    features = forms.MultipleChoiceField(
        choices=[
            ("contact-form", "Contact Form"),
            ("blog", "Blog/News Section"),
            ("user-accounts", "User Accounts"),
            ("payment", "Payment Processing"),
            ("booking", "Online Booking"),
            ("seo", "SEO Optimization"),
        ],
        required=False,
        label="Features Required",
        widget=forms.CheckboxSelectMultiple,
    )

    def clean_features(self):
        features = self.cleaned_data.get("features")
        return ", ".join(features) if features else ""
    

from django import forms
from django.contrib.auth import password_validation
from .models import User

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(required=True, label="Email Address")

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError("No account found for this email.")
        return email

class SetPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="New Password",
        required=True,
        strip=False,
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm New Password",
        required=True,
        strip=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        if password:
            password_validation.validate_password(password)
        return cleaned_data