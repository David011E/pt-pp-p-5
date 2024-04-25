from django.shortcuts import render, redirect, reverse, get_object_or_404
from .models import Product, Category
from allauth.account.models import EmailAddress
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views import View
from django.conf import settings

import stripe
import sweetify

stripe.api_key = 'sk_test_51JZTOFFrxPi5qjzP2uFgNT4yGnmANfbRa0Xb2Fc5ismTeFvdi7BoCSk58T9s52NaCsMzrwdgkCKZzXufLisCi3Rv00D6tt8sx4'

# Create your views here.
def all_services(request):

    products = Product.objects.all()

    templates = 'products/products.html'

    context = {
        'products': products,
        'templates': templates,
    }

    return render(request, templates, context)


class CreateCheckoutSessionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs["pk"]
        product = get_object_or_404(Product, id=product_id)
        YOUR_DOMAIN = "http://localhost:8000/"

        if not request.user.is_authenticated:
            return sweetify("User must be authenticated to initiate checkout.", status=403)
        
        email_address = get_object_or_404(EmailAddress, user=request.user, primary=True).email
        customers = stripe.Customer.list(email=email_address).data

        if customers:
            customer = customers[0]
        else:
            customer = stripe.Customer.create(
                email=email_address,
                metadata={'django_user_id': request.user.id}
            )

        # Check if the user is already subscribed to the product using Stripe API
        if customer:
            subscriptions = stripe.Subscription.list(customer=customer.id)
            for subscription in subscriptions.auto_paging_iter():
                if subscription['status'] == 'active' and subscription['items']['data'][0]['price']['id'] == product.stripe_price_id:
                    sweetify.error(request, "You are already subscribed to this product.")
                    return redirect(reverse('checkout_cancel'))

        checkout_session = stripe.checkout.Session.create(
            client_reference_id=str(request.user.id),
            payment_method_types=['card'],
            mode='subscription',
            customer=customer.id,
            line_items=[
                {
                    'price': product.stripe_price_id,
                    'quantity': 1,
                },
            ],
            metadata={"product_id": str(product.id)},
            success_url=YOUR_DOMAIN + reverse('checkout_success'),
            cancel_url=YOUR_DOMAIN + reverse('checkout_cancel'),
            locale='en',
        )

        checkout_url = checkout_session.url

        return redirect(checkout_url)
    

class checkout_success(TemplateView):
    template_name = "products/checkout_success.html"


class checkout_cancel(TemplateView):
    template_name = 'products/checkout_cancel.html'