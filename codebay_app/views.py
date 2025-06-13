from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from .models import User
from admin_panel.models import Template

from django.shortcuts import render


def index(request):
    # Fetch templates for each section with related images
    latest_templates = Template.objects.filter(status='active').prefetch_related('images').order_by('-created_at')[:9]
    portfolio_templates = Template.objects.filter(status='active', category='portfolio').prefetch_related('images').order_by('-created_at')[:9]
    ecommerce_templates = Template.objects.filter(status='active', category='ecommerce').prefetch_related('images').order_by('-created_at')[:9]
    business_templates = Template.objects.filter(status='active', category='business').prefetch_related('images').order_by('-created_at')[:9]
    popular_templates = Template.objects.filter(status='active').prefetch_related('images').order_by('-downloads')[:9]
    landing_templates = Template.objects.filter(status='active', category='landing-page').prefetch_related('images').order_by('-created_at')[:9]

    # Chunk templates into groups of 3 for carousel slides
    def chunk_list(lst, chunk_size):
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

    context = {
        'latest_templates': chunk_list(latest_templates, 3),
        'portfolio_templates': chunk_list(portfolio_templates, 3),
        'ecommerce_templates': chunk_list(ecommerce_templates, 3),
        'business_templates': chunk_list(business_templates, 3),
        'popular_templates': chunk_list(popular_templates, 3),
        'landing_templates': chunk_list(landing_templates, 3),
    }

    return render(request, 'codebay_app/index.html', context)

from django.shortcuts import render
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Extract form data
            data = form.cleaned_data
            full_name = data['full_name']
            email = data['email']
            phone = data['phone']
            company = data['company']
            website_type = dict(form.fields['website_type'].choices)[data['website_type']]
            budget = dict(form.fields['budget'].choices)[data['budget']]
            timeline = dict(form.fields['timeline'].choices)[data['timeline']] if data['timeline'] else 'Not specified'
            features = data['features'] or 'None'

            # Prepare email content for admin
            admin_subject = f"New Contact Form Submission from {full_name}"
            admin_message = f"""
            New website request submitted:

            Contact Information:
            - Full Name: {full_name}
            - Email: {email}
            - Phone: {phone or 'Not provided'}
            - Company: {company or 'Not provided'}

            Website Requirements:
            - Website Type: {website_type}
            - Budget: {budget}
            - Timeline: {timeline}
            - Features: {features}
            """
            send_mail(
                subject=admin_subject,
                message=admin_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False,
            )

            # Prepare email content for user
            user_subject = "Thank You for Your Website Request!"
            user_message = f"""
            Dear {full_name},

            Thank you for submitting your website request with us! We've received your details and will get back to you within 24-48 hours with an initial proposal.

            Your Submission Details:
            - Full Name: {full_name}
            - Email: {email}
            - Phone: {phone or 'Not provided'}
            - Company: {company or 'Not provided'}
            - Website Type: {website_type}
            - Budget: {budget}
            - Timeline: {timeline}
            - Features: {features}

            Best regards,
            The CodeBay Team
            """
            send_mail(
                subject=user_subject,
                message=user_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, "Your request has been submitted successfully! Check your email for confirmation.")
            return render(request, 'codebay_app/contact.html', {'form': ContactForm()})
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContactForm()

    return render(request, 'codebay_app/contact.html', {'form': form})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from admin_panel.models import Template

def templates_list(request):
    category_filter = request.GET.get('category', '')
    sort_by = request.GET.get('sort', '')
    templates = Template.objects.filter(status='active')

    if category_filter and category_filter != 'all':
        templates = templates.filter(category=category_filter)

    if sort_by == 'popular':
        templates = templates.order_by('-downloads')
    else:
        templates = templates.order_by('-created_at')

    paginator = Paginator(templates, 12)  # 12 templates per page as per your view
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Preprocess technologies for each template in the current page
    for template in page_obj:
        if template.technologies:
            template.tech_list = [tech.strip() for tech in template.technologies.split(',')]
        else:
            template.tech_list = ['Responsive', 'SEO Optimized']  # Default tags

    return render(request, 'codebay_app/templates.html', {
        'templates': page_obj,
        'category_filter': category_filter if category_filter else 'all',  # Ensure 'all' is used if no filter
        'sort_by': sort_by
    })


def template_detail(request, id):
    template = get_object_or_404(Template, id=id, status='active')
    
    # Preprocess technologies
    if template.technologies:
        template.tech_list = [tech.strip() for tech in template.technologies.split(',')]
    else:
        template.tech_list = ['Responsive', 'SEO Optimized']

    # Fetch related templates (same category, exclude current template)
    related_templates = Template.objects.filter(
        category=template.category, status='active'
    ).exclude(id=template.id)[:3]

    return render(request, 'codebay_app/template_detail.html', {
        'template': template,
        'related_templates': related_templates,
    })

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from admin_panel.models import Template

@login_required
def template_instructions_page(request, template_id):
    template = get_object_or_404(Template, id=template_id, status='active')
    return render(request, 'codebay_app/instructions_template.html', {
        'template': template,
    })


def template_action(request, id):
    template = get_object_or_404(Template, id=id)
    messages.info(request, f"Action for template {template.name} not implemented.")
    return redirect('codebay_app:index')



from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from admin_panel.models import BlogPost

def blog(request):
    # Get filter parameters
    category_filter = request.GET.get('category', 'all')

    # Query active blog posts
    blog_posts = BlogPost.objects.filter(status='active')

    # Apply category filter
    if category_filter != 'all':
        blog_posts = blog_posts.filter(category=category_filter)

    # Paginate results (12 posts per page to match frontend)
    paginator = Paginator(blog_posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get all categories for the filter
    categories = BlogPost.CATEGORY_CHOICES

    return render(request, 'codebay_app/blog.html', {
        'blog_posts': page_obj,
        'categories': categories,
        'category_filter': category_filter,
    })

def blog_detail(request, blog_slug):
    blog_post = get_object_or_404(BlogPost, slug=blog_slug, status='active')
    # Get related posts (same category, exclude current post)
    related_posts = BlogPost.objects.filter(
        category=blog_post.category,
        status='active'
    ).exclude(id=blog_post.id)[:3]

    return render(request, 'codebay_app/blog_detail.html', {
        'blog_post': blog_post,
        'related_posts': related_posts,
    })

def register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'codebay_app/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, 'codebay_app/register.html')

        # Create user
        try:
            user = User.objects.create_user(
                email=email,
                full_name=full_name,
                password=password
            )
            login(request, user)
            messages.success(request, "Registration successful! Welcome!")
            # Redirect based on user type
            if user.is_staff:
                return redirect('admin_panel:admin_dashboard')
            return redirect('codebay_app:index')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return render(request, 'codebay_app/register.html')

    return render(request, 'codebay_app/register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            # Redirect based on user type
            if user.is_staff:
                return redirect('admin_panel:admin_dashboard')
            return redirect('codebay_app:user_dashboard')
        else:
            messages.error(request, "Invalid email or password")
            return render(request, 'codebay_app/login.html')

    return render(request, 'codebay_app/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('codebay_app:login')

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from admin_panel.models import Tutorial

def tutorials(request):
    # Get filter and search parameters
    search_query = request.GET.get('search', '')
    # Get query
    category_filter = request.GET.get('category', '')
    # Filter
    type_filter = request.GET.get('type', '')
    filter
    level_filter = request.GET.get('level', '')

    # Query active tutorials
    tutorials = Tutorial.objects.filter(status='active')

    # Apply filters
    if search_query:
        tutorials = tutorials.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    if category_filter:
        tutorials = tutorials.filter(category=category_filter)
    if type_filter:
        tutorials = tutorials.filter(type=type_filter)
    if level_filter:
        tutorials = tutorials.filter(level=level_filter)

    context = {
        'tutorials': tutorials,
        'search_query': search_query,
        'category_filter': category_filter,
        'type_filter': type_filter,
        'level_filter': level_filter,
    }
    return render(request, 'codebay_app/tutorials.html', context)

def tutorial_detail(request, tutorial_id):
    tutorial = get_object_or_404(Tutorial, id=tutorial_id, status='active')
    # Increment views
    tutorial.views += 1
    tutorial.save()
    # Get related tutorials (same category, excluding current)
    related_tutorials = Tutorial.objects.filter(
        category=tutorial.category,
        status='active'
    ).exclude(id=tutorial_id)[:3]

    context = {
        'tutorial': tutorial,
        'related_tutorials': related_tutorials,
    }
    return render(request, 'codebay_app/tutorial_detail.html', context)


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from admin_panel.models import Template, UserActivity

@login_required
def download_template_file(request, template_id):
    template = get_object_or_404(Template, id=template_id, status='active')
    
    # Check if the user has already downloaded this template
    has_downloaded = UserActivity.objects.filter(
        user=request.user,
        template=template,
        action="Downloaded Template",
        status="completed"
    ).exists()
    
    if not has_downloaded:
        # Increment the download count
        template.downloads += 1
        template.save()
        
        # Log the user activity
        UserActivity.objects.create(
            user=request.user,
            template=template,
            action="Downloaded Template",
            status="completed",
            date=timezone.now()
        )
    
    # Redirect to the actual file URL to initiate the download
    if template.zip_file:
        return redirect(template.zip_file.url)
    else:
        # Handle case where ZIP file is missing
        return redirect('codebay_app:template_instructions_page', template_id=template.id)
    

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from admin_panel.models import UserActivity

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from admin_panel.models import UserActivity, Order

@login_required
def user_dashboard(request):
    # Count total downloaded templates by the user
    total_downloads = UserActivity.objects.filter(
        user=request.user,
        action="Downloaded Template",
        status="completed"
    ).count()

    # Fetch user's orders
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]  # Limit to 5 for display

    return render(request, 'codebay_app/dashboard.html', {
        'total_downloads': total_downloads,
        'orders': orders,
    })


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from .models import User, Profile

class UserProfileForm(forms.Form):
    full_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'id': 'name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'id': 'email'}))
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)
    profile_picture = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'id': 'profile_picture', 'accept': 'image/*'}))

@login_required
def user_settings(request):
    if request.method == 'POST':
        # Handle Profile Update
        if 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, request.FILES)
            if profile_form.is_valid():
                user = request.user
                # Check if email is changed and not already taken by another user
                new_email = profile_form.cleaned_data['email']
                if new_email != user.email and User.objects.filter(email=new_email).exists():
                    messages.error(request, "This email is already in use.")
                    return redirect('codebay_app:user_settings')
                
                user.full_name = profile_form.cleaned_data['full_name']
                user.email = new_email
                user.bio = profile_form.cleaned_data['bio']
                user.save()
                
                # Update or create profile for profile picture
                profile, created = Profile.objects.get_or_create(user=user)
                if profile_form.cleaned_data['profile_picture']:
                    profile.profile_picture = profile_form.cleaned_data['profile_picture']
                    profile.save()
                
                messages.success(request, "Profile updated successfully!")
                return redirect('codebay_app:user_settings')
            else:
                for field, errors in profile_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")

        # Handle Password Change
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Keep the user logged in after password change
                messages.success(request, "Password changed successfully!")
                return redirect('codebay_app:user_settings')
            else:
                for field, errors in password_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")
    else:
        profile_form = UserProfileForm(initial={
            'full_name': request.user.full_name,
            'email': request.user.email,
            'bio': request.user.bio,
        })
        password_form = PasswordChangeForm(user=request.user)

    return render(request, 'codebay_app/settings.html', {
        'profile_form': profile_form,
        'password_form': password_form,
    })

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from admin_panel.models import UserActivity

@login_required
def downloaded_templates(request):
    # Fetch templates the user has downloaded
    user_downloads = UserActivity.objects.filter(
        user=request.user,
        action="Downloaded Template",
        status="completed"
    ).select_related('template').order_by('-date')

    return render(request, 'codebay_app/downloaded_templates.html', {
        'user_downloads': user_downloads,
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from admin_panel.models import Template, Cart, CartItem, Order, OrderItem

@login_required
def cart_add(request, id):
    template = get_object_or_404(Template, id=id, status='active')
    
    # Get or create the user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Check if the template is already in the cart
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, template=template)
    
    if not item_created:
        # If the item already exists, increment the quantity
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"Updated quantity of {template.name} in your cart.")
    else:
        messages.success(request, f"{template.name} added to your cart.")
    
    return redirect('codebay_app:cart_detail')

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'codebay_app/cart_detail.html', {'cart': cart})

@login_required
def cart_remove(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    template_name = cart_item.template.name
    
    if request.method == 'POST':
        cart_item.delete()
        messages.success(request, f"{template_name} removed from your cart.")
    return redirect('codebay_app:cart_detail')

@login_required
def cart_update_quantity(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, f"Updated quantity for {cart_item.template.name}.")
        else:
            cart_item.delete()
            messages.success(request, f"{cart_item.template.name} removed from your cart.")
    return redirect('codebay_app:cart_detail')

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    if not cart.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('codebay_app:cart_detail')
    
    if request.method == 'POST':
        # Create a new order
        order = Order.objects.create(user=request.user, total_amount=cart.total_price)
        
        # Add items to the order
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                template=item.template,
                quantity=item.quantity,
                price=item.template.price
            )
        
        # Clear the cart
        cart.items.all().delete()
        messages.success(request, "Checkout successful! Your order has been placed.")
        return redirect('codebay_app:user_dashboard')  # Redirect to dashboard or order confirmation
    
    return render(request, 'codebay_app/checkout.html', {'cart': cart})

@login_required
def buy_now(request, template_id):
    template = get_object_or_404(Template, id=template_id, status='active')
    
    # Create a temporary cart for buy now
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.items.all().delete()  # Clear existing items for "Buy Now"
    
    # Add the single template to the cart
    CartItem.objects.create(cart=cart, template=template, quantity=1)
    
    return redirect('codebay_app:checkout')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from .models import User, PasswordResetToken
from .forms import PasswordResetRequestForm, SetPasswordForm

def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email, is_active=True)
            # Delete existing tokens for this user
            PasswordResetToken.objects.filter(user=user).delete()
            # Create new token
            token = PasswordResetToken(user=user)
            token.save()
            # Send reset email
            reset_url = request.build_absolute_uri(
                reverse('codebay_app:password_reset_confirm', kwargs={'token': token.token})
            )
            subject = "Password Reset Request"
            message = f"""
            Dear {user.full_name},

            You requested a password reset. Click the link below to reset your password:
            {reset_url}

            This link will expire in 15 minutes. If you didn't request this, please ignore this email.

            Best regards,
            The CodeBay Team
            """
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, "A password reset link has been sent to your email.")
            return redirect('codebay_app:password_reset_success')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'codebay_app/reset_password_request.html', {'form': form})

def password_reset_success(request):
    return render(request, 'codebay_app/reset_password_success.html')

def password_reset_confirm(request, token):
    token_obj = get_object_or_404(PasswordResetToken, token=token)
    if not token_obj.is_valid():
        messages.error(request, "This reset link has expired. Please request a new one.")
        return redirect('codebay_app:password_reset_request')
    
    if request.method == 'POST':
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            user = token_obj.user
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Delete all tokens for this user
            PasswordResetToken.objects.filter(user=user).delete()
            messages.success(request, "Your password has been reset successfully. Please log in.")
            return redirect('codebay_app:login')  # Adjust to your login URL
    else:
        form = SetPasswordForm()
    return render(request, 'codebay_app/reset_password_reset.html', {'form': form, 'token': token})