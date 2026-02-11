from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import UserRegisterForm, UserUpdateForm, UserProfileForm
from .models import UserProfile
from movies.models import FavoriteMovie, FavoriteSeries, FavoriteShow



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
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    accepted_privacy = profile_obj.accepted_privacy
    accepted_terms = profile_obj.accepted_terms
    accepted_at = profile_obj.accepted_at.strftime('%d.%m.%Y %H:%M') if profile_obj.accepted_at else None

    if request.method == 'POST':
        # чекбоксы приходят только если отмечены
        accepted_privacy_post = request.POST.get('accepted_privacy') == 'on'
        accepted_terms_post = request.POST.get('accepted_terms') == 'on'

        if accepted_privacy_post and accepted_terms_post:
            profile_obj.accepted_at = timezone.now()
            messages.success(request, 'Согласия сохранены.')
        else:
            profile_obj.accepted_at = None
            messages.info(request, 'Согласия сняты.')

        profile_obj.accepted_privacy = accepted_privacy_post
        profile_obj.accepted_terms = accepted_terms_post
        profile_obj.save(update_fields=['accepted_privacy', 'accepted_terms', 'accepted_at'])

        return redirect('users:profile')

    context = {
        'accepted_privacy': accepted_privacy,
        'accepted_terms': accepted_terms,
        'accepted_at': accepted_at,
    }
    return render(request, 'users/profile.html', context)


@login_required
def favorites(request):
    favorite_movies = (
        FavoriteMovie.objects.filter(user=request.user)
        .select_related('movie')
        .order_by('-created_at')
    )
    favorite_series = (
        FavoriteSeries.objects.filter(user=request.user)
        .select_related('series')
        .order_by('-created_at')
    )
    favorite_shows = (
        FavoriteShow.objects.filter(user=request.user)
        .select_related('show')
        .order_by('-created_at')
    )
    return render(
        request,
        'users/favorites.html',
        {
            'favorite_movies': favorite_movies,
            'favorite_series': favorite_series,
            'favorite_shows': favorite_shows,
        },
    )


@login_required
def profile_edit(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        if 'save_profile' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            profile_form = UserProfileForm(request.POST, request.FILES, instance=profile_obj)
            password_form = PasswordChangeForm(request.user)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Профиль обновлён.')
                return redirect('users:profile_edit')
        elif 'change_password' in request.POST:
            user_form = UserUpdateForm(instance=request.user)
            profile_form = UserProfileForm(instance=profile_obj)
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Пароль обновлён.')
                return redirect('users:profile_edit')
        else:
            user_form = UserUpdateForm(instance=request.user)
            profile_form = UserProfileForm(instance=profile_obj)
            password_form = PasswordChangeForm(request.user)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile_obj)
        password_form = PasswordChangeForm(request.user)

    return render(
        request,
        'users/profile_edit.html',
        {
            'user_form': user_form,
            'profile_form': profile_form,
            'password_form': password_form,
        },
    )

