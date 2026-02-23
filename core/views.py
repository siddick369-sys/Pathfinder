from django.shortcuts import render


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
