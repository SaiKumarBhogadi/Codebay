from django.urls import path
from . import views


app_name = 'codebay_app'
urlpatterns = [
   
    path('', views.index, name='home'),
       path('contact/', views.contact, name='contact'),
        path('templates/', views.templates_list, name='templates_list'),
        path('template/<int:id>/', views.template_detail, name='template_detail'),
        path('template/<int:template_id>/instructions/', views.template_instructions_page, name='template_instructions_page'),
        path('template/<int:template_id>/download-file/', views.download_template_file, name='download_template_file'),
        path('template-action/<int:id>/', views.template_action, name='template_action'),
        path('cart/add/<int:id>/', views.cart_add, name='cart_add'),
       path('blog/', views.blog, name='blog'),
        path('blog/<slug:blog_slug>/', views.blog_detail, name='blog_detail'),
       path('register/', views.register, name='register'),
       path('login/', views.login_view, name='login'),
       path('logout/', views.logout_view, name='logout'),
      path('tutorials/', views.tutorials, name='tutorials'),
        path('tutorials/<int:tutorial_id>/', views.tutorial_detail, name='tutorial_detail'),
        path('dashboard/',views.user_dashboard, name='user_dashboard'),
        path('settings',views.user_settings, name='user_settings'),
        path('downloaded_templates/',views.downloaded_templates, name='downloaded_templates'),


        path('cart/add/<int:id>/', views.cart_add, name='cart_add'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:item_id>/', views.cart_update_quantity, name='cart_update_quantity'),
    path('checkout/', views.checkout, name='checkout'),
    path('buy-now/<int:template_id>/', views.buy_now, name='buy_now'),


    path('forgot-password/', views.password_reset_request, name='password_reset_request'),
    path('reset/success/', views.password_reset_success, name='password_reset_success'),
    path('reset/<uuid:token>/', views.password_reset_confirm, name='password_reset_confirm'),
       
]