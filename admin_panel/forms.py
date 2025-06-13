from django import forms
from django import forms
from django.forms import inlineformset_factory
from .models import Template, TemplateImage, TemplateScreenshot, Feature, Review, FAQ

class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = [
            'name', 'category', 'price', 'status', 'preview_url',
            'description', 'why_choose', 'technologies',
            'rating', 'rating_count', 'zip_file', 'installation_instructions'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter template name'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Enter price'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'preview_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Enter description'}),
            'why_choose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Why choose this template?'}),
            'technologies': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., HTML, CSS, JS'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '5', 'placeholder': '0.0 to 5.0'}),
            'rating_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Number of ratings'}),
            'zip_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'installation_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'e.g., 1. Unzip the file.\n2. Open index.html in a browser.'}),
        }
        labels = {
            'name': 'Template Name',
            'category': 'Category',
            'price': 'Price (Rs)',
            'status': 'Status',
            'preview_url': 'Preview URL',
            'description': 'Description',
            'why_choose': 'Why Choose This Template',
            'technologies': 'Technologies',
            'rating': 'Rating (0.0–5.0)',
            'rating_count': 'Rating Count',
            'zip_file': 'Upload ZIP File',
            'installation_instructions': 'Installation and Running Instructions',
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating < 0 or rating > 5:
            raise forms.ValidationError("Rating must be between 0.0 and 5.0.")
        return rating

# Inline formset for Template Images
TemplateImageFormSet = inlineformset_factory(
    Template, TemplateImage,
    fields=['image', 'alt_text'],
    extra=2,
    can_delete=True,
    widgets={
        'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        'alt_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Template Preview'}),
    }
)

# Inline formset for Template Screenshots
TemplateScreenshotFormSet = inlineformset_factory(
    Template, TemplateScreenshot,
    fields=['image', 'caption'],
    extra=2,
    can_delete=True,
    widgets={
        'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Desktop View'}),
    }
)

# Inline formset for Features
FeatureFormSet = inlineformset_factory(
    Template, Feature,
    fields=['name', 'description', 'icon'],
    extra=2,
    can_delete=True,
    widgets={
        'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Responsive Design'}),
        'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g., Looks stunning on all devices.'}),
        'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., bi bi-display'}),
    }
)

# Inline formset for Reviews
ReviewFormSet = inlineformset_factory(
    Template, Review,
    fields=['author', 'rating', 'comment'],
    extra=1,
    can_delete=True,
    widgets={
        'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., John Doe'}),
        'rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '5'}),
        'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    }
)

# Inline formset for FAQs
FAQFormSet = inlineformset_factory(
    Template, FAQ,
    fields=['question', 'answer'],
    extra=1,
    can_delete=True,
    widgets={
        'question': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Is this template responsive?'}),
        'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    }
)



from django import forms
from .models import Tutorial
import datetime
import re

class TutorialForm(forms.ModelForm):
    duration = forms.CharField(
        max_length=5,
        help_text="Enter duration in mm:ss format (e.g., 15:30)",
        widget=forms.TextInput(attrs={'pattern': r'\d{1,2}:\d{2}'})
    )

    class Meta:
        model = Tutorial
        fields = ['thumbnail', 'title', 'category', 'level', 'type', 'status', 'video_url', 'content', 'description', 'duration']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter tutorial title'}),
            'video_url': forms.URLInput(attrs={'placeholder': 'https://example.com/video'}),
            'content': forms.Textarea(attrs={'placeholder': 'Enter text content for the tutorial', 'rows': 10}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter a brief description of the tutorial', 'rows': 4}),
        }

    def clean_duration(self):
        duration_str = self.cleaned_data['duration']
        if not re.match(r'^\d{1,2}:\d{2}$', duration_str):
            raise forms.ValidationError("Duration must be in mm:ss format (e.g., 15:30)")
        try:
            minutes, seconds = map(int, duration_str.split(':'))
            if seconds >= 60:
                raise forms.ValidationError("Seconds must be less than 60")
            if minutes < 0 or seconds < 0:
                raise forms.ValidationError("Duration cannot be negative")
            return datetime.timedelta(minutes=minutes, seconds=seconds)
        except ValueError:
            raise forms.ValidationError("Invalid duration format")

    def clean_video_url(self):
        video_url = self.cleaned_data.get('video_url')
        type_value = self.cleaned_data.get('type')
        if type_value == 'video' and not video_url:
            raise forms.ValidationError("Video URL is required for video tutorials")
        if video_url and not video_url.startswith(('http://', 'https://')):
            raise forms.ValidationError("Video URL must start with http:// or https://")
        return video_url

    def clean_content(self):
        content = self.cleaned_data.get('content')
        type_value = self.cleaned_data.get('type')
        if type_value == 'text' and not content:
            raise forms.ValidationError("Content is required for text tutorials")
        return content
    



from django import forms
from codebay_app.models import User

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'bio']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if email is already taken by another user
        user_id = self.instance.id if self.instance else None
        if User.objects.exclude(id=user_id).filter(email=email).exists():
            raise forms.ValidationError("This email is already registered by another user.")
        return email

class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput, label="Current Password")
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm New Password")

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError("Current password is incorrect.")
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("New password and confirm password do not match.")
        if new_password and not new_password.strip():
            raise forms.ValidationError("New password cannot be empty.")

        return cleaned_data
    

from django import forms
from .models import BlogPost

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'category', 'status', 'featured_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter blog title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Write your blog content here'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'featured_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Get request to set author
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.pk:  # If creating a new blog post
            instance.author = self.request.user
        if commit:
            instance.save()
        return instance