"""pt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import handler404
from products.views import (
    CreateCheckoutSessionView,
    checkout_cancel,
    StripeWebhookView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('home.urls')),
    path('products/', include('products.urls')),
    path('userprofile/', include('userprofile.urls')),
    path('about/', include('about.urls')),
    path('result/', include('result.urls')),
    path('contact/', include('contact.urls')),
    path('create-checkout-session/<pk>/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('checkout_cancel/', checkout_cancel.as_view(), name='checkout_cancel'), 
    path('webhook/stripe/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('handler404/', handler404),  # Use the handler404 view directly
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
