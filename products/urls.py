from django.urls import path
from . import views

urlpatterns = [
    path('', views.AllServicesView.as_view(), name='products'),
    path('<int:product_id>/', views.product_details, name='product_details'),
    path('add/', views.add_product, name='add_product'), 
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'), 
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'), 
    path('cancellation_policy/<int:product_id>/', views.cancellation_policy, name='cancellation_policy'),
]
