from django.shortcuts import render, redirect, reverse, get_object_or_404
from .models import Review 
from .forms import ReviewForm

import sweetify

# Create your views here.
def results(request):
    """
    A view to return index page with reviews
    """
    reviews = Review.objects.all()  # Fetch all reviews
    context = {
        'reviews': reviews,
    }
    return render(request, 'result/result.html', context)


def add_review(request):
    """ Add a review to the store """

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            sweetify.success(request, 'Successfully added review!')
            return redirect(reverse('result'))
        else:
            sweetify.error(request, 'Failed to add review. Please ensure the form is valid.')
    else:
        form = ReviewForm()

    form = ReviewForm()
    template = 'result/add_review.html'
    context = {
        'form': form
    }

    return render(request, template, context)


def review_details(request, reviews_id):
    """
    A view to show individual review details
    """

    review = get_object_or_404(Review, pk=reviews_id)  # Retrieve a single review object

    context = {
        'review': review,  # Pass the single review object to the template with the correct key
    }

    return render(request, 'result/review_details.html', context)
