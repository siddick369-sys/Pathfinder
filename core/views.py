from django.shortcuts import render
from django.views.decorators.cache import cache_control


def home(request):
    return render(request, 'core/index.html')

def mentions_legales(request):
    return render(request, 'core/mentions.html')

def rgpd(request):
    return render(request, 'core/rgpd.html')

def faq(request):
    return render(request, 'core/faq.html')

def contact(request):
    return render(request, 'core/contact.html')

@cache_control(max_age=0, no_cache=True)
def offline(request):
    return render(request, 'core/offline.html')

def service_worker(request):
    """Sert le service worker depuis la racine du domaine."""
    import os
    from django.http import HttpResponse
    sw_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'sw.js')
    with open(sw_path, 'r') as f:
        return HttpResponse(f.read(), content_type='application/javascript')
