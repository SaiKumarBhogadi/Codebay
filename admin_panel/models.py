from django.db import models

class Template(models.Model):
    CATEGORY_CHOICES = [
        ('portfolio', 'Portfolio'),
        ('ecommerce', 'E-commerce'),
        ('business', 'Business'),
        ('landing-page', 'Landing Page'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    preview_url = models.URLField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    why_choose = models.TextField(blank=True, help_text="Why choose this template?")
    downloads = models.PositiveIntegerField(default=0)
    technologies = models.CharField(max_length=200, blank=True)
    rating = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    zip_file = models.FileField(upload_to='templates/zips/', blank=True, null=True, help_text="Upload the ZIP file for this template")
    installation_instructions = models.TextField(blank=True, help_text="Instructions to install and run this template")

    def __str__(self):
        return self.name

    def get_rating_stars(self):
        try:
            rating = float(self.rating)
            full_stars = int(rating)
            half_star = 1 if rating - full_stars >= 0.5 else 0
            empty_stars = 5 - full_stars - half_star
            return {
                'full': range(full_stars),
                'half': range(half_star),
                'empty': range(empty_stars)
            }
        except (ValueError, TypeError):
            return {'full': range(0), 'half': range(0), 'empty': range(5)}

class TemplateImage(models.Model):
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/')
    alt_text = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Image for {self.template.name}"

class TemplateScreenshot(models.Model):
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='screenshots')
    image = models.ImageField(upload_to='screenshots/')
    caption = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Screenshot for {self.template.name}"

class Feature(models.Model):
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='features')
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Bootstrap icon class, e.g., 'bi bi-display'")

    def __str__(self):
        return f"{self.name} for {self.template.name}"

class Review(models.Model):
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='reviews')
    author = models.CharField(max_length=100)
    rating = models.FloatField(default=0.0)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.author} for {self.template.name}"

    def get_rating_stars(self):
        try:
            rating = float(self.rating)
            full_stars = int(rating)
            half_star = 1 if rating - full_stars >= 0.5 else 0
            empty_stars = 5 - full_stars - half_star
            return {
                'full': range(full_stars),
                'half': range(half_star),
                'empty': range(empty_stars)
            }
        except (ValueError, TypeError):
            return {'full': range(0), 'half': range(0), 'empty': range(5)}

class FAQ(models.Model):
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=200)
    answer = models.TextField()

    def __str__(self):
        return f"FAQ: {self.question} for {self.template.name}"


from django.db import models
from django.utils import timezone

class Tutorial(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('draft', 'Draft'),
    ]
    CATEGORY_CHOICES = [
        ('web-development', 'Web Development'),
        ('programming', 'Programming'),
        ('design', 'Design'),
    ]
    TYPE_CHOICES = [
        ('video', 'Video'),
        ('text', 'Text'),
    ]
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='video')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    duration = models.DurationField()  # Stored as timedelta
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    thumbnail = models.ImageField(upload_to='tutorials/images/', null=True, blank=True)
    video_url = models.URLField(max_length=200, blank=True)
    content = models.TextField(blank=True)  # For text-based tutorials
    description = models.TextField(blank=True)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_duration_display(self):
        total_seconds = int(self.duration.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    

from django.conf import settings
from django.utils import timezone
class UserActivity(models.Model):
    STATUS_CHOICES = (
        ('completed', 'Completed'),
        ('pending', 'Pending'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    action = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.status}"
    

from django.db import models
from django.utils import timezone
from django.urls import reverse
from codebay_app.models import User  # Reference your custom User model

class BlogPost(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    CATEGORY_CHOICES = (
        ('technology', 'Technology'),
        ('web-design', 'Web Design'),
        ('development', 'Development'),
        ('tutorials', 'Tutorials'),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    featured_image = models.ImageField(upload_to='uploads/blog_images/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
            # Ensure slug is unique
            original_slug = self.slug
            counter = 1
            while BlogPost.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('codebay_app:blog_detail', kwargs={'blog_slug': self.slug})
    

from django.db import models
from django.utils import timezone
from django.conf import settings
from .models import Template  # Reference the existing Template model

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.email}"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.template.name} in cart"

    @property
    def subtotal(self):
        return self.quantity * self.template.price

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.email}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of purchase

    def __str__(self):
        return f"{self.quantity} x {self.template.name} in Order {self.order.id}"

    @property
    def subtotal(self):
        return self.quantity * self.price