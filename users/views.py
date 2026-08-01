from django.contrib.auth import get_user_model, login, logout, update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail
from django.urls import reverse
from django.http import HttpResponse, Http404
import os

from .forms import (
    LoginForm,
    UserProfileForm,
    CommunityForm,
    CommunityEditForm,
    UserRegisterForm,
    UserUpdateForm,
    _normalize_ru_phone,
)
from .models import UserProfile, Community
from movies.models import FavoriteMovie, FavoriteSeries, FavoriteShow


User = get_user_model()


def register_view(request):
    """Регистрация пользователя"""
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Регистрация прошла успешно! Добро пожаловать!')
            return redirect('users:profile')
    else:
        user_form = UserRegisterForm()

    return render(
        request,
        'users/register.html',
        {'user_form': user_form}
    )


def logout_view(request):
    """Простой logout через GET"""
    logout(request)
    return redirect('movies:index')


def privacy(request):
    """Скачивание файла политики конфиденциальности с редиректом на главную"""
    file_path = os.path.join('Documents', 'Политика_конфиденциальности.docx')
    
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
    except FileNotFoundError:
        raise Http404("Файл не найден")
    
    # Преобразуем бинарные данные в base64 для JavaScript
    import base64
    file_b64 = base64.b64encode(file_content).decode('utf-8')
    
    # Создаем HTML страницу с JavaScript для скачивания файла и редиректа
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Скачивание файла</title>
        <meta charset="utf-8">
        <meta http-equiv="refresh" content="2; url=/">
    </head>
    <body>
        <p>Скачивание файла... Через 2 секунды вы будете перенаправлены на главную страницу.</p>
        <script>
            // Создаем blob из base64 данных
            var byteCharacters = atob('{file_b64}');
            var byteNumbers = new Array(byteCharacters.length);
            for (var i = 0; i < byteCharacters.length; i++) {{
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }}
            var byteArray = new Uint8Array(byteNumbers);
            var blob = new Blob([byteArray], {{type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}});
            
            // Создаем ссылку для скачивания
            var link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = 'Политика_конфиденциальности.docx';
            
            // Кликаем по ссылке для скачивания
            document.body.appendChild(link);
            link.click();
        </script>
    </body>
    </html>
    """
    
    return HttpResponse(html_content, content_type='text/html')


def terms(request):
    """Скачивание файла пользовательского соглашения с редиректом на главную"""
    file_path = os.path.join('Documents', 'Пользовательское_соглашение.docx')
    
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
    except FileNotFoundError:
        raise Http404("Файл не найден")
    
    # Преобразуем бинарные данные в base64 для JavaScript
    import base64
    file_b64 = base64.b64encode(file_content).decode('utf-8')
    
    # Создаем HTML страницу с JavaScript для скачивания файла и редиректа
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Скачивание файла</title>
        <meta charset="utf-8">
        <meta http-equiv="refresh" content="2; url=/">
    </head>
    <body>
        <p>Скачивание файла... Через 2 секунды вы будете перенаправлены на главную страницу.</p>
        <script>
            // Создаем blob из base64 данных
            var byteCharacters = atob('{file_b64}');
            var byteNumbers = new Array(byteCharacters.length);
            for (var i = 0; i < byteCharacters.length; i++) {{
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }}
            var byteArray = new Uint8Array(byteNumbers);
            var blob = new Blob([byteArray], {{type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}});
            
            // Создаем ссылку для скачивания
            var link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = 'Пользовательское_соглашение.docx';
            
            // Кликаем по ссылке для скачивания
            document.body.appendChild(link);
            link.click();
        </script>
    </body>
    </html>
    """
    
    return HttpResponse(html_content, content_type='text/html')


def data_processing_consent(request):
    """Скачивание файла согласия на обработку персональных данных с редиректом на главную"""
    file_path = os.path.join('Documents', 'Согласие_обработки_персональных_данных.docx')
    
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
    except FileNotFoundError:
        raise Http404("Файл не найден")
    
    # Преобразуем бинарные данные в base64 для JavaScript
    import base64
    file_b64 = base64.b64encode(file_content).decode('utf-8')
    
    # Создаем HTML страницу с JavaScript для скачивания файла и редиректа
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Скачивание файла</title>
        <meta charset="utf-8">
        <meta http-equiv="refresh" content="2; url=/">
    </head>
    <body>
        <p>Скачивание файла... Через 2 секунды вы будете перенаправлены на главную страницу.</p>
        <script>
            // Создаем blob из base64 данных
            var byteCharacters = atob('{file_b64}');
            var byteNumbers = new Array(byteCharacters.length);
            for (var i = 0; i < byteCharacters.length; i++) {{
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }}
            var byteArray = new Uint8Array(byteNumbers);
            var blob = new Blob([byteArray], {{type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}});
            
            // Создаем ссылку для скачивания
            var link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = 'Согласие_обработки_персональных_данных.docx';
            
            // Кликаем по ссылке для скачивания
            document.body.appendChild(link);
            link.click();
        </script>
    </body>
    </html>
    """
    
    return HttpResponse(html_content, content_type='text/html')

@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    accepted_privacy = profile_obj.accepted_privacy
    accepted_terms = profile_obj.accepted_terms
    accepted_data_processing = profile_obj.accepted_data_processing
    accepted_at = profile_obj.accepted_at.strftime('%d.%m.%Y %H:%M') if profile_obj.accepted_at else None

    if request.method == 'POST':
        # чекбоксы приходят только если отмечены
        accepted_privacy_post = request.POST.get('accepted_privacy') == 'on'
        accepted_terms_post = request.POST.get('accepted_terms') == 'on'
        accepted_data_processing_post = request.POST.get('accepted_data_processing') == 'on'

        if accepted_privacy_post and accepted_terms_post and accepted_data_processing_post:
            profile_obj.accepted_at = timezone.now()
            messages.success(request, 'Согласия сохранены.')
        else:
            profile_obj.accepted_at = None
            messages.info(request, 'Согласия сняты.')

        profile_obj.accepted_privacy = accepted_privacy_post
        profile_obj.accepted_terms = accepted_terms_post
        profile_obj.accepted_data_processing = accepted_data_processing_post
        profile_obj.save(update_fields=['accepted_privacy', 'accepted_terms', 'accepted_data_processing', 'accepted_at'])

        return redirect('users:profile')

    context = {
        'accepted_privacy': accepted_privacy,
        'accepted_terms': accepted_terms,
        'accepted_data_processing': accepted_data_processing,
        'accepted_at': accepted_at,
    }
    return render(request, 'users/profile.html', context)


@login_required
def profile_edit(request):
    """Редактирование профиля"""
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


@login_required
def create_community(request):
    """Создание нового сообщества"""
    # Проверяем права пользователя
    if not request.user.profile.can_create_community:
        messages.error(request, 'У вас нет прав для создания сообществ. Обратитесь к администратору.')
        return redirect('users:profile')
    
    if request.method == 'POST':
        form = CommunityForm(request.POST, request.FILES)
        if form.is_valid():
            community = form.save(commit=False)
            community.created_by = request.user
            community.save()
            community.members_users.add(request.user)
            messages.success(request, f'Сообщество "{community.name}" успешно создано!')
            return redirect('movies:community_detail', community_id=community.id)
    else:
        form = CommunityForm()
    
    return render(request, 'users/create_community.html', {'form': form})


@login_required
def edit_community(request, community_id):
    """Редактирование сообщества"""
    community = get_object_or_404(
        Community.objects.select_related('created_by')
        .prefetch_related('members_users'),
        id=community_id
    )
    
    # Проверяем права: только создатель может редактировать
    if community.created_by != request.user:
        messages.error(request, 'Вы можете редактировать только свои сообщества.')
        return redirect('movies:community_detail', community_id=community.id)
    
    if request.method == 'POST':
        form = CommunityEditForm(request.POST, request.FILES, instance=community)
        if form.is_valid():
            form.save()
            messages.success(request, f'Сообщество "{community.name}" успешно обновлено!')
            return redirect('movies:community_detail', community_id=community.id)
    else:
        form = CommunityEditForm(instance=community)
    
    return render(request, 'users/edit_community.html', {
        'form': form,
        'community': community,
    })


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
def manage_community(request, community_id):
    """Управление проектами сообщества"""
    from movies.models import Movie, Series, Show, CommunityProject
    
    community = get_object_or_404(
        Community.objects.select_related('created_by')
        .prefetch_related('members_users', 'communityproject_set__movie', 'communityproject_set__series', 'communityproject_set__show')
        .distinct(),
        id=community_id
    )
    
    # Проверяем права: только создатель может управлять проектами
    if community.created_by != request.user:
        messages.error(request, 'Вы можете управлять проектами только в своих сообществах.')
        return redirect('movies:community_detail', community_id=community.id)
    
    # Получаем все проекты сообщества
    community_projects = CommunityProject.objects.filter(community=community).select_related(
        'movie', 'series', 'show'
    )
    
    # Получаем все доступные фильмы, сериалы, шоу
    movies = Movie.objects.filter(is_active=True).order_by('title')
    series = Series.objects.filter(is_active=True).order_by('title')
    shows = Show.objects.filter(is_active=True).order_by('title')
    
    if request.method == 'POST':
        project_type = request.POST.get('project_type')
        project_id = request.POST.get('project_id')
        
        if project_type and project_id:
            try:
                if project_type == 'movie':
                    movie = Movie.objects.get(id=project_id)
                    CommunityProject.objects.get_or_create(
                        community=community,
                        movie=movie,
                        defaults={'series': None, 'show': None}
                    )
                    messages.success(request, f'Фильм "{movie.title}" добавлен к сообществу!')
                elif project_type == 'series':
                    series_obj = Series.objects.get(id=project_id)
                    CommunityProject.objects.get_or_create(
                        community=community,
                        series=series_obj,
                        defaults={'movie': None, 'show': None}
                    )
                    messages.success(request, f'Сериал "{series_obj.title}" добавлен к сообществу!')
                elif project_type == 'show':
                    show_obj = Show.objects.get(id=project_id)
                    CommunityProject.objects.get_or_create(
                        community=community,
                        show=show_obj,
                        defaults={'movie': None, 'series': None}
                    )
                    messages.success(request, f'Шоу "{show_obj.title}" добавлено к сообществу!')
            except (Movie.DoesNotExist, Series.DoesNotExist, Show.DoesNotExist):
                messages.error(request, 'Проект не найден.')
    
    # Получаем уже добавленные проекты
    existing_projects = {
        'movies': [p.movie for p in community_projects if p.movie],
        'series': [p.series for p in community_projects if p.series],
        'shows': [p.show for p in community_projects if p.show],
    }
    
    context = {
        'community': community,
        'movies': movies,
        'series': series,
        'shows': shows,
        'existing_projects': existing_projects,
    }
    return render(request, 'users/manage_community.html', context)


@login_required
def manage_members(request, community_id):
    """Управление участниками сообщества"""
    community = get_object_or_404(
        Community.objects.select_related('created_by')
        .prefetch_related('members_users'),
        id=community_id
    )
    
    # Проверяем права: только создатель может управлять участниками
    if community.created_by != request.user:
        messages.error(request, 'Вы можете управлять участниками только в своих сообществах.')
        return redirect('movies:community_detail', community_id=community.id)
    
    # Получаем всех пользователей для поиска
    all_users = User.objects.all().order_by('username')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        
        if action and user_id:
            try:
                user_to_manage = User.objects.get(id=user_id)
                
                if action == 'add':
                    community.members_users.add(user_to_manage)
                    messages.success(request, f'Пользователь "{user_to_manage.username}" добавлен в сообщество!')
                elif action == 'remove':
                    community.members_users.remove(user_to_manage)
                    messages.success(request, f'Пользователь "{user_to_manage.username}" удален из сообщества!')
            except User.DoesNotExist:
                messages.error(request, 'Пользователь не найден.')
    
    # Текущие участники
    current_members = community.members_users.all()
    
    # Доступные пользователи (не участники)
    available_users = all_users.exclude(id__in=current_members.values_list('id', flat=True))
    
    context = {
        'community': community,
        'current_members': current_members,
        'available_users': available_users,
    }
    return render(request, 'users/manage_members.html', context)
