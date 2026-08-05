from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/',        admin.site.urls),
    path('', TemplateView.as_view(template_name='landingpage.html'), name='landing'),    
    path('order/',        include('ordering_service.urls')),
    path('user/',         include('user.urls')),
    path('googleaccount/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
