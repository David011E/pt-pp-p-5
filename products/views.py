from django.shortcuts import render, redirect, reverse, get_object_or_404
from .models import Product, Category
from allauth.account.models import EmailAddress
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.db.models.functions import Lower
from django.views.generic import TemplateView
from django.views import View
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

import stripe
import sweetify

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
def all_services(request):

    products = Product.objects.all()

    query = None
    categories = None

    if request.GET:
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                sweetify.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('all_services'))

            
            queries = Q(name__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query)
            products = products.filter(queries)
    
    context = {
        "products": products,
        'search_term': query,
        'current_categories': categories,
    }
    return render(request, 'products/products.html', context)


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
            success_url=YOUR_DOMAIN + reverse('userprofile'),
            cancel_url=YOUR_DOMAIN + reverse('checkout_cancel'),
            locale='en',
        )

        checkout_url = checkout_session.url

        return redirect(checkout_url)
    

class checkout_cancel(TemplateView):
    template_name = 'products/checkout_cancel.html'


class StripeWebhookView(View):
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(StripeWebhookView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET  # Replace 'whsec_...' with your actual webhook signing secret

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            return HttpResponse(status=400)

        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            # Handle the checkout session completion
            handle_checkout_session(session)

        # Respond to Stripe that the webhook was received
        return JsonResponse({'status': 'success'})
    
def handle_checkout_session(session):
    # Implement your business logic here
    print("Checkout session completed with session ID:", session['id'])