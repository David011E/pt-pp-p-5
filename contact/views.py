from django.shortcuts import render

# Create your views here.
def contact(request):
    """ Contact me form """
    
    template = 'contact/contact.html'
    
    return render(request, template)