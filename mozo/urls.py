"""mozo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

from api import mongo_views, views
from mozo import settings

service_router = routers.SimpleRouter()
service_router.register(r'', mongo_views.ServiceAreaViewSet, '')

provider_router = routers.SimpleRouter()
provider_router.register(r'', views.ProviderViewSet, '')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^providers/signup/$', views.SignUpView.as_view()),
    url(r'^providers/signin/$', views.SignInView.as_view()),
    url(r'^service-areas/', include(service_router.urls)),
    url(r'^providers/', include(provider_router.urls)),
    url(r'^docs/', include_docs_urls(title='Mozo', schema_url=settings.CORE_API_SCHEMA_URL))
]
