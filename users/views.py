from django.contrib.auth import login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import UserRegisterForm



def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('users:profile')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('movies:index')  # или 'users:login'

def privacy(request):
    return render(request, 'users/privacy.html')

def terms(request):
    return render(request, 'users/terms.html')

@login_required
def profile(request):
    # читаем согласия из cookies
    accepted_privacy = request.COOKIES.get('accepted_privacy') == 'true'
    accepted_terms = request.COOKIES.get('accepted_terms') == 'true'
    accepted_at = request.COOKIES.get('accepted_at')  # строка с датой или None

    if request.method == 'POST':
        # чекбоксы приходят только если отмечены
        accepted_privacy_post = request.POST.get('accepted_privacy') == 'on'
        accepted_terms_post = request.POST.get('accepted_terms') == 'on'

        response = redirect('users:profile')

        # записываем куки на год
        max_age = 60 * 60 * 24 * 365  # 1 год
        response.set_cookie('accepted_privacy', 'true' if accepted_privacy_post else 'false', max_age=max_age)
        response.set_cookie('accepted_terms', 'true' if accepted_terms_post else 'false', max_age=max_age)

        if accepted_privacy_post and accepted_terms_post:
            now_str = timezone.now().strftime('%d.%m.%Y %H:%M')
            response.set_cookie('accepted_at', now_str, max_age=max_age)
            messages.success(request, 'Согласия сохранены.')
        else:
            response.delete_cookie('accepted_at')
            messages.info(request, 'Согласия сняты.')

        return response

    context = {
        'accepted_privacy': accepted_privacy,
        'accepted_terms': accepted_terms,
        'accepted_at': accepted_at,
    }
    return render(request, 'users/profile.html', context)

