from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Feedback
from django.contrib import messages
from django.shortcuts import redirect


@login_required
def feedback_view(request):
    if request.method == 'POST':
        subject = request.POST.get('subject', '')
        message_text = request.POST.get('message', '')
        rating = int(request.POST.get('rating', 5))
        Feedback.objects.create(user=request.user, subject=subject, message=message_text, rating=rating)
        messages.success(request, 'Merci pour votre retour !')
        return redirect('accounts:dashboard')
    return render(request, 'feedback/form.html')
