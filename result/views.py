from django.shortcuts import render, redirect, reverse, get_object_or_404
from .models import Review 
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required

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


@login_required
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


@login_required
def edit_review(request, reviews_id):
    """ Edit a review in the store """

    if not request.user.is_superuser:
        sweetify.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    review = get_object_or_404(Review, pk=reviews_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES, instance=review)  # Assigning to 'form' here
        if form.is_valid():  # Changed from 'if form.is_valid():'
            form.save()
            sweetify.success(request, 'Successfully updated review!')
            return redirect(reverse('review_details', args=[review.id]))
        else:
            sweetify.error(request, 'Failed to update review. Please ensure the form is valid.')
    else:
        form = ReviewForm(instance=review)
        sweetify.info(request, f'You are editing {review.name}')

    template = 'result/edit_review.html'
    context = {
        'form': form,
        'review': review,
    }

    return render(request, template, context)


@login_required
def delete_review(request, reviews_id):
    """ Delete a product in the store """

    if not request.user.is_superuser:
        sweetify.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
    
    review = get_object_or_404(Review, pk=reviews_id)
    review.delete()
    sweetify.success(request, 'Review deleted!')
    return redirect(reverse('result'))