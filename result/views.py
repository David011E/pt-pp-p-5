from django.shortcuts import render
from .models import Review 

def results(request):
    """
    A view to return index page with reviews
    """
    reviews = Review.objects.all()  # Fetch all reviews
    context = {
        'reviews': reviews,
    }
    return render(request, 'result/result.html', context)