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
from .forms import ProductForm
from django.contrib.auth.decorators import login_required

import stripe
import sweetify

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
class AllServicesView(View):
    def get(self, request, *args, **kwargs):
        # Retrieve all products
        products = Product.objects.all()
        
        categories = None
        query = None
        
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if query:
            queries = Q(name__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query)
            products = products.filter(queries)
            if not products.exists():
                messages.error(request, "No products found matching your criteria!")
                return redirect('all_services')
        
         # Initialize subscribed products list
        subscribed_product_names = []
        if request.user.is_authenticated:
            # Attempt to retrieve the Stripe customer
            stripe_customer = stripe.Customer.list(email=request.user.email).data
            if stripe_customer:
                customer_id = stripe_customer[0].id
                subscriptions = stripe.Subscription.list(customer=customer_id)
                for subscription in subscriptions.auto_paging_iter():
                    price_id = subscription['items']['data'][0]['price']['id']
                    price = stripe.Price.retrieve(price_id)
                    product = stripe.Product.retrieve(price.product)
                    subscribed_product_names.append(product.name)

        # Check each product to see if it matches any subscribed product names
        for product in products:
            product.is_subscribed = product.name in subscribed_product_names

        context = {
            'products': products,
            'search_term': query,
            'current_categories': categories,
            'subscribed_product_names': subscribed_product_names,
        }
        
        return render(request, 'products/products.html', context)


def product_details(request, product_id):
    """
    A view to show individual service details
    """

    product = get_object_or_404(Product, pk=product_id)  # Retrieve a single service object

    context = {
        'product': product,  # Pass the single service object to the template
    }

    return render(request, 'products/product_details.html', context)  


class CreateCheckoutSessionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs["pk"]
        product = get_object_or_404(Product, id=product_id)
        YOUR_DOMAIN = "https://pt-pp-p-5-acaa98cb0828.herokuapp.com"

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


@login_required
def add_product(request):
    """ Add a product to the store """

    if not request.user.is_superuser:
        sweetify.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            sweetify.success(request, 'Successfully added product!')
            return redirect(reverse('product_details', args=[product.id]))
        else:
            sweetify.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()
        
    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """ Edit a product in the store """

    if not request.user.is_superuser:
        sweetify.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            sweetify.success(request, 'Successfully updated product!')
            return redirect(reverse('product_details', args=[product.id]))
        else:
            sweetify.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        sweetify.info(request, f'You are editing {product.name}')


    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    """ Delete a product in the store """

    if not request.user.is_superuser:
        sweetify.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
    
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    sweetify.success(request, 'Product deleted!')
    return redirect(reverse('products'))



def cancellation_policy(request, product_id):
    """
    A view to show individual service details
    """

    product = get_object_or_404(Product, pk=product_id)  # Retrieve a single service object

    context = {
        'product': product,  # Pass the single service object to the template
    }

    return render(request, 'products/cancellation_policy.html', context)  