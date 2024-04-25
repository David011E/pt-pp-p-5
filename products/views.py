from django.shortcuts import render
from .models import Product, Category

# Create your views here.
def all_services(request):

    products = Product.objects.all()

    templates = 'products/products.html'

    context = {
        'products': products,
        'templates': templates,
    }

    return render(request, templates, context)