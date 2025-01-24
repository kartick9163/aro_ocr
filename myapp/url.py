from django.urls import path
from myapp import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('email_vrfy', views.email_vrfy, name='email_vrfy'),
    path('register', views.register, name='register'),
    path('vrfy_html', views.vrfy_html, name='vrfy_html'),
    path('preference', views.usr_preference, name='preference'),
    path('role', views.user_role, name='role'),
    path('resend_email', views.resend_mail, name='resend_email'),
    path('api_key', views.generate_apikey, name='generate_apikey'),
    path('fetch_api_key', views.fetch_api, name='fetch_api_key'),
    path('delete_key', views.delete_api_key, name='delete_api_key'),
    # path('upload', views.upload, name='upload'),
    # path('uploads', views.uploads, name='uploads'),
]