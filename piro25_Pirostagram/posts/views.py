from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, Comment, Story, StoryImage
from .forms import PostForm, CommentForm
from django.db.models import Count

@login_required
def feed(request):
    followings = request.user.followings.all()
    posts = Post.objects.filter(author__in=followings) | Post.objects.filter(author=request.user)
    sort = request.GET.get('sort', 'latest')
    if sort == 'like':
        posts = posts.annotate(like_count=Count('like_users')).order_by('-like_count')
    elif sort == 'comment':
        posts = posts.annotate(comment_count=Count('comments')).order_by('-comment_count')
    else:
        posts = posts.order_by('-created_at')
    comment_form = CommentForm()
    stories = Story.objects.filter(author__in=followings) | Story.objects.filter(author=request.user)
    stories = stories.order_by('-created_at')
    return render(request, 'posts/feed.html', {'posts': posts, 'comment_form': comment_form, 'stories': stories})

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:feed')
    else:
        form = PostForm()
    return render(request, 'posts/post_form.html', {'form': form})

@login_required
def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return redirect('posts:feed')
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:feed')
    else:
        form = PostForm(instance=post)
    return render(request, 'posts/post_form.html', {'form': form})

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author == request.user:
        post.delete()
    return redirect('posts:feed')

@login_required
def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.like_users.all():
        post.like_users.remove(request.user)
    else:
        post.like_users.add(request.user)
    return redirect('posts:feed')

@login_required
def comment_create(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    return redirect('posts:feed')

@login_required
def comment_update(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author != request.user:
        return redirect('posts:feed')
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('posts:feed')
    else:
        form = CommentForm(instance=comment)
    return render(request, 'posts/comment_form.html', {'form': form})

@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author == request.user:
        comment.delete()
    return redirect('posts:feed')

@login_required
def story_create(request):
    if request.method == 'POST':
        images = request.FILES.getlist('images')
        if images:
            story = Story.objects.create(author=request.user)
            for image in images:
                StoryImage.objects.create(story=story, image=image)
            return redirect('posts:feed')
    return render(request, 'posts/story_form.html')


@login_required
def story_detail(request, pk):
    story = get_object_or_404(Story, pk=pk)
    return render(request, 'posts/story_detail.html', {'story': story})

@login_required
def story_delete(request, pk):
    story = get_object_or_404(Story, pk=pk)
    if story.author == request.user:
        story.delete()
    return redirect('posts:feed')

@login_required
def post_search(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        results = Post.objects.filter(content__icontains=query).order_by('-created_at')
    return render(request, 'posts/post_search.html', {
        'query': query,
        'results': results,
    })