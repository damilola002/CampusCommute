from django.urls import path
from . import views 
#from django.conf.urls.defaults import *
app_name = 'user'
urlpatterns = [
    path('', views.home_redirect, name='home_redirect'),
    path('home/', views.home_redirect, name='home_redirect_alt'),
    path('login/', views.login_user, name='login'),
    path('signup/', views.register_user, name='signup'),
    path('profile/', views.profile_view, name='profile'),
    path('verify-2fa/', views.verify_2fa, name='verify_2fa'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('logout/', views.logout_user, name='logout'),
]
