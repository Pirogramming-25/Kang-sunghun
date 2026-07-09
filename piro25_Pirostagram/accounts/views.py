from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import SignupForm
from .models import User

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('posts:feed')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = profile_user.posts.all().order_by('-created_at')
    return render(request, 'accounts/profile.html', {
        'profile_user': profile_user,
        'posts': posts,
    })

@login_required
def user_search(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        results = User.objects.filter(
            Q(username__icontains=query) | Q(nickname__icontains=query)
        )
    return render(request, 'accounts/user_search.html', {
        'query': query,
        'results': results,
    })

@login_required
def follow(request, username):
    target = get_object_or_404(User, username=username)
    if target != request.user:
        if target in request.user.followings.all():
            request.user.followings.remove(target)
        else:
            request.user.followings.add(target)
    return redirect('accounts:profile', username=username)