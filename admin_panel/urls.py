from django.urls import path
from . import views


app_name = 'admin_panel'
urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
   
    path('users/', views.users_list, name='users_list'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),

    path('templates/', views.templates_list, name='templates_list'),
    path('templates/add/', views.templates_add, name='templates_add'),
    path('templates/edit/<int:template_id>/', views.templates_edit, name='templates_edit'),
    path('templates/toggle/<int:template_id>/', views.templates_toggle, name='templates_toggle'),
    path('templates/delete/<int:template_id>/', views.templates_delete, name='templates_delete'),

    path('tutorials/', views.tutorials_list, name='tutorials_list'),
    path('tutorials/add/', views.tutorials_add, name='tutorials_add'),
    path('tutorials/edit/<int:tutorial_id>/', views.tutorials_edit, name='tutorials_edit'),
    path('tutorials/toggle/<int:tutorial_id>/', views.tutorials_toggle, name='tutorials_toggle'),
    path('tutorials/delete/<int:tutorial_id>/', views.tutorials_delete, name='tutorials_delete'),

    path('blogs/', views.admin_blog_list, name='admin_blog_list'),
    path('blogs/add/', views.admin_blog_add, name='admin_blog_add'),
    path('blogs/edit/<int:blog_id>/', views.admin_blog_edit, name='admin_blog_edit'),
    path('blogs/delete/<int:blog_id>/', views.admin_blog_delete, name='admin_blog_delete'),
    path('blogs/toggle-status/<int:blog_id>/', views.admin_blog_toggle_status, name='admin_blog_toggle_status'),

    path('orders/', views.admin_orders_list, name='admin_orders_list'),
    path('orders/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('orders/update-status/<int:order_id>/', views.admin_order_update_status, name='admin_order_update_status'),

    path('admin-settings/', views.settings, name='settings'),

    
   
]