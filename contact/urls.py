from django.urls import path
from . import views

urlpatterns = [
    path('', views.contact, name='contact'),
    path('contact_admin/', views.contact_admin, name='contact_admin'),
    path('contact_details/<int:contact_id>/', views.contact_details, name='contact_details'),
    path('delete/<int:contact_id>/', views.delete_message, name='delete_message'),
]
