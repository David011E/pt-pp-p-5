from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from allauth.account.models import EmailAddress
from django.conf import settings

import stripe
import sweetify

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
class UserProfileView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Retrieve the user's primary email address
        email_address_object = EmailAddress.objects.filter(user=request.user, primary=True).first()
        if not email_address_object:
            sweetify.error(request, "Email address not found.")
            return redirect(reverse('home'))  # Redirect to home if email address not found

        # Get the actual email string from the email address object
        email_address = email_address_object.email

        # Retrieve the customer from Stripe using the email address
        customers = stripe.Customer.list(email=email_address).data
        if not customers:
            sweetify.error(request, "Stripe customer not found for the provided email address.")
            return redirect(reverse('home'))
        
        customer = customers[0]  # Assume the first customer is the correct one

        # Retrieve the user's subscriptions from Stripe
        subscriptions = stripe.Subscription.list(customer=customer.id)

        # Parse subscription data to extract relevant information
        user_subscriptions = []
        for subscription in subscriptions.auto_paging_iter():
            product_id = subscription['items']['data'][0]['price']['product']
            product = stripe.Product.retrieve(product_id)  # Retrieve product details

            # Get the product image URL, default to an empty string if not available
            product_image_url = product['images'][0] if product.get('images') else ""

            user_subscriptions.append({
                'id': subscription['id'],
                'status': subscription['status'],
                'product_name': product['name'],  # Use the retrieved product name
                'product_image_url': product_image_url  # Include the image URL
            })

        # Render the user profile template with the user's subscriptions
        return render(request, 'userprofile/userprofile.html', {'user_subscriptions': user_subscriptions})