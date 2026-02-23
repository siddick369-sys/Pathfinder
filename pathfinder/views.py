from django.shortcuts import render
from django.http import Http404
from django.template import TemplateDoesNotExist

def serve_html(request, page='index'):
    template_name = f"{page}.html"
    try:
        return render(request, template_name)
    except TemplateDoesNotExist:
        raise Http404("Page not found")
