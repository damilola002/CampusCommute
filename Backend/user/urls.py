from django.urls import path
from . import views 
#from django.conf.urls.defaults import *
app_name = 'user'
urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('signup/', views.register_user, name='signup'),
]
