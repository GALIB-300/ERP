"""
URL configuration for django_binp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),                
    path('accounts/', include('accounts.urls')),   
    path('accounts/', include('django.contrib.auth.urls')),  
    path('customerdetailed/', include('customerdetailed.urls')),
    path('salesmarketing/', include('salesmarketing.urls')),
    path('project/', include('project.urls')),
    path('construction/', include('construction.urls')),
    path('resource/', include('resource.urls')),
    path('supplier/', include('supplier.urls')),
    path('po/', include('po.urls')),
    path('requisition/', include('requisition.urls')),
    path('ws/', include('ws.urls')),
    path('casting/', include('casting.urls')),
    path('price_event/', include('price_event.urls')),
    path('rbp/', include('rbp.urls')),
    path('rip/', include('rip.urls')),
    path('company/', include('company.urls')),
    path("rwc/", include("rwc.urls")),
    path('pr/', include('pr.urls')),
    path('stc/', include('stc.urls')),
    path('proposal/', include('proposal.urls')),
    path("pfp/", include("pfp.urls")), 
    path("pt/", include("pt.urls")),
    path("client/", include("client.urls")),
    path("ctv/", include("ctv.urls")),
    path("cba/", include("cba.urls")),
    path("letter/", include("letter.urls")),
    path("sb/", include("sb.urls")),
    
]
