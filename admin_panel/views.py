from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.apps import apps
from django.utils import timezone
from .models import Template, UserActivity, Tutorial
from codebay_app.models import User
from .forms import TemplateForm, TemplateImageFormSet, TemplateScreenshotFormSet, FeatureFormSet, ReviewFormSet, FAQFormSet, TutorialForm, ProfileForm, PasswordChangeForm
from django.core.paginator import Paginator

def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get the custom user model dynamically
    User = apps.get_model('codebay_app', 'User')

    # Get current date and time
    current_time = timezone.now()

    # Calculate total users
    total_users = User.objects.count()

    # Calculate active templates
    active_templates = Template.objects.filter(status='active').count()

    # Get recent activities (last 3)
    recent_activities = UserActivity.objects.select_related('user', 'template').order_by('-date')[:3]

    context = {
        'current_time': current_time,
        'total_users': total_users,
        'active_templates': active_templates,
        'recent_activities': recent_activities,
    }
    return render(request, 'admin_panel/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def users_list(request):
    search_query = request.GET.get('search', '')
    users = User.objects.all()
    
    if search_query:
        users = users.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    return render(request, 'admin_panel/users.html', {
        'users': users,
        'search_query': search_query
    })

@login_required
@user_passes_test(is_admin)
def add_user(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        is_staff = request.POST.get('is_staff') == 'on'
        is_active = request.POST.get('is_active') == 'on'

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, 'admin_panel/add_user.html', {'full_name': full_name, 'email': email})

        try:
            user = User.objects.create_user(
                email=email,
                full_name=full_name,
                password=password,
                is_staff=is_staff,
                is_active=is_active
            )
            # Log the activity
            UserActivity.objects.create(
                user=request.user,
                action=f"Added User: {user.full_name}",
                status="completed",
                date=timezone.now()
            )
            messages.success(request, f"User {full_name} created successfully!")
            return redirect('admin_panel:users_list')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return render(request, 'admin_panel/add_user.html', {'full_name': full_name, 'email': email})

    return render(request, 'admin_panel/add_user.html')

@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        is_staff = request.POST.get('is_staff') == 'on'
        is_active = request.POST.get('is_active') == 'on'

        if User.objects.exclude(id=user_id).filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, 'admin_panel/edit_user.html', {'user': user})

        try:
            user.full_name = full_name
            user.email = email
            user.is_staff = is_staff
            user.is_active = is_active
            if request.POST.get('password'):
                user.set_password(request.POST.get('password'))
            user.save()
            # Log the activity
            UserActivity.objects.create(
                user=request.user,
                action=f"Edited User: {user.full_name}",
                status="completed",
                date=timezone.now()
            )
            messages.success(request, f"User {full_name} updated successfully!")
            return redirect('admin_panel:users_list')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return render(request, 'admin_panel/edit_user.html', {'user': user})

    return render(request, 'admin_panel/edit_user.html', {'user': user})

@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        if user == request.user:
            messages.error(request, "You cannot delete your own account")
            return redirect('admin_panel:users_list')
        full_name = user.full_name
        user.delete()
        # Log the activity
        UserActivity.objects.create(
            user=request.user,
            action=f"Deleted User: {full_name}",
            status="completed",
            date=timezone.now()
        )
        messages.success(request, f"User {full_name} deleted successfully!")
        return redirect('admin_panel:users_list')
    return redirect('admin_panel:users_list')

@login_required
@user_passes_test(is_admin)
def templates_list(request):
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    
    templates = Template.objects.all()
    if search_query:
        templates = templates.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    if category_filter:
        templates = templates.filter(category=category_filter)
    
    total_templates = templates.count()
    active_templates = templates.filter(status='active').count()
    priced_templates = templates.filter(price__gt=0).count()
    
    paginator = Paginator(templates, 10)  # 10 templates per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin_panel/templates.html', {
        'templates': page_obj,
        'total_templates': total_templates,
        'active_templates': active_templates,
        'priced_templates': priced_templates,
        'search_query': search_query,
        'category_filter': category_filter,
    })

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import TemplateForm, TemplateImageFormSet, TemplateScreenshotFormSet, FeatureFormSet, ReviewFormSet, FAQFormSet
from .models import UserActivity
from .decorators import user_passes_test

def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
def templates_add(request):
    if request.method == 'POST':
        form = TemplateForm(request.POST, request.FILES)
        image_formset = TemplateImageFormSet(request.POST, request.FILES, instance=None, prefix='image')
        screenshot_formset = TemplateScreenshotFormSet(request.POST, request.FILES, instance=None, prefix='screenshot')
        feature_formset = FeatureFormSet(request.POST, instance=None, prefix='feature')
        review_formset = ReviewFormSet(request.POST, instance=None, prefix='review')
        faq_formset = FAQFormSet(request.POST, instance=None, prefix='faq')

        if (form.is_valid() and image_formset.is_valid() and screenshot_formset.is_valid() and 
            feature_formset.is_valid() and review_formset.is_valid() and faq_formset.is_valid()):
            template = form.save()
            image_formset.instance = template
            screenshot_formset.instance = template
            feature_formset.instance = template
            review_formset.instance = template
            faq_formset.instance = template
            image_formset.save()
            screenshot_formset.save()
            feature_formset.save()
            review_formset.save()
            faq_formset.save()
            # Log the activity
            UserActivity.objects.create(
                user=request.user,
                template=template,
                action="Added Template",
                status="completed",
                date=timezone.now()
            )
            messages.success(request, f"Template {template.name} added successfully!")
            return redirect('admin_panel:templates_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TemplateForm()
        image_formset = TemplateImageFormSet(instance=None, prefix='image')
        screenshot_formset = TemplateScreenshotFormSet(instance=None, prefix='screenshot')
        feature_formset = FeatureFormSet(instance=None, prefix='feature')
        review_formset = ReviewFormSet(instance=None, prefix='review')
        faq_formset = FAQFormSet(instance=None, prefix='faq')

    return render(request, 'admin_panel/add_template.html', {
        'form': form,
        'image_formset': image_formset,
        'screenshot_formset': screenshot_formset,
        'feature_formset': feature_formset,
        'review_formset': review_formset,
        'faq_formset': faq_formset,
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import TemplateForm, TemplateImageFormSet, TemplateScreenshotFormSet, FeatureFormSet, ReviewFormSet, FAQFormSet
from admin_panel.models import Template, UserActivity
from .decorators import user_passes_test

def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
def templates_edit(request, template_id):
    template = get_object_or_404(Template.objects.prefetch_related(
        'images', 'screenshots', 'features', 'reviews', 'faqs'
    ), id=template_id)
    if request.method == 'POST':
        form = TemplateForm(request.POST, request.FILES, instance=template)
        image_formset = TemplateImageFormSet(request.POST, request.FILES, instance=template, prefix='image')
        screenshot_formset = TemplateScreenshotFormSet(request.POST, request.FILES, instance=template, prefix='screenshot')
        feature_formset = FeatureFormSet(request.POST, instance=template, prefix='feature')
        review_formset = ReviewFormSet(request.POST, instance=template, prefix='review')
        faq_formset = FAQFormSet(request.POST, instance=template, prefix='faq')

        if (form.is_valid() and image_formset.is_valid() and screenshot_formset.is_valid() and 
            feature_formset.is_valid() and review_formset.is_valid() and faq_formset.is_valid()):
            form.save()
            image_formset.save()
            screenshot_formset.save()
            feature_formset.save()
            review_formset.save()
            faq_formset.save()
            # Log the activity
            UserActivity.objects.create(
                user=request.user,
                template=template,
                action="Updated Template",
                status="completed",
                date=timezone.now()
            )
            messages.success(request, f"Template {template.name} updated successfully!")
            return redirect('admin_panel:templates_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TemplateForm(instance=template)
        image_formset = TemplateImageFormSet(instance=template, prefix='image')
        screenshot_formset = TemplateScreenshotFormSet(instance=template, prefix='screenshot')
        feature_formset = FeatureFormSet(instance=template, prefix='feature')
        review_formset = ReviewFormSet(instance=template, prefix='review')
        faq_formset = FAQFormSet(instance=template, prefix='faq')

    return render(request, 'admin_panel/edit_template.html', {
        'form': form,
        'image_formset': image_formset,
        'screenshot_formset': screenshot_formset,
        'feature_formset': feature_formset,
        'review_formset': review_formset,
        'faq_formset': faq_formset,
        'template': template,
    })

@login_required
@user_passes_test(is_admin)
def templates_toggle(request, template_id):
    template = get_object_or_404(Template, id=template_id)
    if request.method == 'POST':
        old_status = template.status
        template.status = 'inactive' if template.status == 'active' else 'active'
        template.save()
        # Log the activity
        UserActivity.objects.create(
            user=request.user,
            template=template,
            action=f"Changed Template Status: {old_status} to {template.status}",
            status="completed",
            date=timezone.now()
        )
        messages.success(request, f"Template {template.name} status updated to {template.get_status_display()}!")
    return redirect('admin_panel:templates_list')

@login_required
@user_passes_test(is_admin)
def templates_delete(request, template_id):
    template = get_object_or_404(Template, id=template_id)
    if request.method == 'POST':
        template_name = template.name
        template.delete()
        # Log the activity
        UserActivity.objects.create(
            user=request.user,
            action=f"Deleted Template: {template_name}",
            status="completed",
            date=timezone.now()
        )
        messages.success(request, f"Template {template_name} deleted successfully!")
    return redirect('admin_panel:templates_list')

@login_required
@user_passes_test(is_admin)
def tutorials_list(request):
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    
    tutorials = Tutorial.objects.all()
    if search_query:
        tutorials = tutorials.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    if category_filter:
        tutorials = tutorials.filter(category=category_filter)
    
    total_tutorials = tutorials.count()
    active_tutorials = tutorials.filter(status='active').count()
    draft_tutorials = tutorials.filter(status='draft').count()
    video_tutorials = Tutorial.objects.filter(type='video').count()
    text_tutorials = Tutorial.objects.filter(type='text').count()
    
    paginator = Paginator(tutorials, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin_panel/tutorials.html', {
        'tutorials': page_obj,
        'total_tutorials': total_tutorials,
        'active_tutorials': active_tutorials,
        'draft_tutorials': draft_tutorials,
        'video_tutorials': video_tutorials,
        'text_tutorials': text_tutorials,
        'search_query': search_query,
        'category_filter': category_filter,
    })

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.utils import timezone
from .forms import TutorialForm
from .models import UserActivity

def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
def tutorials_add(request):
    if request.method == 'POST':
        form = TutorialForm(request.POST, request.FILES)
        if form.is_valid():
            tutorial = form.save()
            UserActivity.objects.create(
                user=request.user,
                action=f"Added Tutorial: {tutorial.title} ({tutorial.get_type_display()})",
                status="completed",
                date=timezone.now()
            )
            messages.success(request, f"Tutorial '{tutorial.title}' added successfully!")
            return redirect('admin_panel:tutorials_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TutorialForm()
    return render(request, 'admin_panel/add_tutorial.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def tutorials_edit(request, tutorial_id):
    tutorial = get_object_or_404(Tutorial, id=tutorial_id)
    if request.method == 'POST':
        form = TutorialForm(request.POST, request.FILES, instance=tutorial)
        if form.is_valid():
            tutorial = form.save()
            # Log the activity
            UserActivity.objects.create(
                user=request.user,
                action=f"Updated Tutorial: {tutorial.title}",
                status="completed",
                date=timezone.now()
            )
            messages.success(request, f"Tutorial {tutorial.title} updated successfully!")
            return redirect('admin_panel:tutorials_list')
    else:
        form = TutorialForm(instance=tutorial, initial={'duration': tutorial.get_duration_display()})
    return render(request, 'admin_panel/edit_tutorial.html', {'form': form, 'tutorial': tutorial})

@login_required
@user_passes_test(is_admin)
def tutorials_toggle(request, tutorial_id):
    tutorial = get_object_or_404(Tutorial, id=tutorial_id)
    if request.method == 'POST':
        old_status = tutorial.status
        if tutorial.status == 'active':
            tutorial.status = 'inactive'
        elif tutorial.status == 'draft':
            tutorial.status = 'active'
        else:
            tutorial.status = 'active'
        tutorial.save()
        # Log the activity
        UserActivity.objects.create(
            user=request.user,
            action=f"Changed Tutorial Status: {old_status} to {tutorial.status}",
            status="completed",
            date=timezone.now()
        )
        messages.success(request, f"Tutorial {tutorial.title} status updated to {tutorial.get_status_display()}!")
    return redirect('admin_panel:tutorials_list')

@login_required
@user_passes_test(is_admin)
def tutorials_delete(request, tutorial_id):
    tutorial = get_object_or_404(Tutorial, id=tutorial_id)
    if request.method == 'POST':
        tutorial_title = tutorial.title
        tutorial.delete()
        # Log the activity
        UserActivity.objects.create(
            user=request.user,
            action=f"Deleted Tutorial: {tutorial_title}",
            status="completed",
            date=timezone.now()
        )
        messages.success(request, f"Tutorial {tutorial_title} deleted successfully!")
    return redirect('admin_panel:tutorials_list')


@login_required
@user_passes_test(is_admin)
def settings(request):
    profile_form = ProfileForm(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        if 'update_profile' in request.POST:  # Profile Settings form
            profile_form = ProfileForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                # Log the activity
                UserActivity.objects.create(
                    user=request.user,
                    action="Updated Profile",
                    status="completed",
                    date=timezone.now()
                )
                messages.success(request, "Profile updated successfully!")
            else:
                messages.error(request, "Please correct the errors below.")

        elif 'update_password' in request.POST:  # Account Settings form
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                request.user.set_password(password_form.cleaned_data['new_password'])
                request.user.save()
                # Log the activity
                UserActivity.objects.create(
                    user=request.user,
                    action="Updated Password",
                    status="completed",
                    date=timezone.now()
                )
                messages.success(request, "Password updated successfully! Please log in again.")
                return redirect('login')  # Redirect to login page after password change
            else:
                messages.error(request, "Please correct the errors below.")

    return render(request, 'admin_panel/settings.html', {
        'profile_form': profile_form,
        'password_form': password_form,
    })



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BlogPost
from .forms import BlogPostForm

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, redirect
from admin_panel.models import BlogPost

@login_required
def admin_blog_list(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('codebay_app:index')

    # Get search and category filter parameters
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    
    # Fetch blog posts
    blog_posts = BlogPost.objects.all()
    
    # Apply search filter
    if search_query:
        blog_posts = blog_posts.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Apply category filter
    if category_filter:
        blog_posts = blog_posts.filter(category=category_filter)
    
    # Order by created_at (descending)
    blog_posts = blog_posts.order_by('-created_at')
    
    # Calculate counts for stats section
    total_blogs = blog_posts.count()
    active_blogs = blog_posts.filter(status='active').count()
    inactive_blogs = blog_posts.filter(status='inactive').count()
    
    # Pagination
    paginator = Paginator(blog_posts, 10)  # 10 blogs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get category choices for filter dropdown
    categories = BlogPost._meta.get_field('category').choices
    
    # Context for template
    context = {
        'blog_posts': page_obj,
        'total_blogs': total_blogs,
        'active_blogs': active_blogs,
        'inactive_blogs': inactive_blogs,
        'search_query': search_query,
        'category_filter': category_filter,
        'categories': categories,
    }
    
    return render(request, 'admin_panel/blog_list.html', context)

@login_required
def admin_blog_add(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('codebay_app:index')

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, "Blog post added successfully!")
            return redirect('admin_panel:admin_blog_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BlogPostForm(request=request)

    return render(request, 'admin_panel/blog_add.html', {'form': form})

@login_required
def admin_blog_edit(request, blog_id):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('codebay_app:index')

    blog_post = get_object_or_404(BlogPost, id=blog_id)
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=blog_post, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, "Blog post updated successfully!")
            return redirect('admin_panel:admin_blog_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BlogPostForm(instance=blog_post, request=request)

    return render(request, 'admin_panel/blog_edit.html', {'form': form, 'blog_post': blog_post})

@login_required
def admin_blog_delete(request, blog_id):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('codebay_app:index')

    blog_post = get_object_or_404(BlogPost, id=blog_id)
    if request.method == 'POST':
        blog_post.delete()
        messages.success(request, "Blog post deleted successfully!")
        return redirect('admin_panel:admin_blog_list')
    return redirect('admin_panel:admin_blog_list')

@login_required
def admin_blog_toggle_status(request, blog_id):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('codebay_app:index')

    blog_post = get_object_or_404(BlogPost, id=blog_id)
    if request.method == 'POST':
        blog_post.status = 'inactive' if blog_post.status == 'active' else 'active'
        blog_post.save()
        messages.success(request, f"Blog post status updated to {blog_post.status}!")
    return redirect('admin_panel:admin_blog_list')


from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Order

@login_required
def admin_orders_list(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('codebay_app:index')

    # Get search and status filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    # Fetch orders
    orders = Order.objects.all()
    
    # Apply search filter (by user's full_name or email)
    if search_query:
        orders = orders.filter(
            Q(user__full_name__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    # Apply status filter
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Order by created_at (descending)
    orders = orders.order_by('-created_at')
    
    # Calculate counts for stats section
    total_orders = orders.count()
    pending_orders = orders.filter(status='pending').count()
    completed_orders = orders.filter(status='completed').count()
    cancelled_orders = orders.filter(status='cancelled').count()
    
    # Pagination
    paginator = Paginator(orders, 10)  # 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get status choices for filter dropdown
    status_choices = Order.STATUS_CHOICES
    
    # Context for template
    context = {
        'orders': page_obj,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': status_choices,
    }
    
    return render(request, 'admin_panel/orders_list.html', context)

@login_required
def admin_order_detail(request, order_id):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('codebay_app:index')

    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin_panel/order_detail.html', {'order': order})

@login_required
def admin_order_update_status(request, order_id):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('codebay_app:index')

    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f"Order status updated to {order.status}.")
        else:
            messages.error(request, "Invalid status selected.")
    return redirect('admin_panel:admin_orders_list')