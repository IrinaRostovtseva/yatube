from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import (require_GET, require_http_methods,
                                          require_POST)

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


@require_GET
def index(request):
    post_list = Post.objects.prefetch_related('author').order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator
    }
    return render(request, 'index.html', context)


@login_required(login_url='/auth/login/')
@require_GET
def follow_index(request):
    post_list = Post.objects.filter(
        author__following__user=request.user).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator
    }
    return render(request, 'index.html', context)


@login_required(login_url='/auth/login/')
@require_GET
def profile_follow(request, username):
    if request.user.username == username:
        return redirect('profile', username=username)
    following = User.objects.get(username=username)
    is_follow = Follow.objects.filter(
        user=request.user, author=following).exists()
    if is_follow:
        return redirect('profile_unfollow', username=username)
    Follow.objects.create(user=request.user, author=following)
    return redirect('profile', username=username)


@login_required
@require_GET
def profile_unfollow(request, username):
    follow = Follow.objects.filter(
        user=request.user, author__username=username)
    if not follow:
        return redirect('profile_follow', username=username)
    follow.delete()
    return redirect('profile', username=username)


@require_GET
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.select_related('author', 'group').filter(
        group=group).order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page_num = request.GET.get('page')
    page = paginator.get_page(page_num)
    context = {
        'group': group,
        'paginator': paginator,
        'page': page
    }
    return render(request, 'group.html', context)


@login_required(login_url='/auth/login/')
@require_POST
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'new_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.text = form.cleaned_data['text']
    post.group = form.cleaned_data['group']
    post.save()
    return redirect('index')


@require_GET
def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=user_profile).exists()
    posts = Post.objects.select_related('author').filter(
        author=user_profile).order_by('-pub_date')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'user_profile': user_profile,
        'page': page,
        'paginator': paginator,
        'following': following,
    }
    return render(request, 'profile.html', context)


@require_GET
def post_view(request, username, post_id):
    user_profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    comments = Comment.objects.filter(post=post_id).order_by('-created')
    following = False
    if request.user.is_authenticated:
        Follow.objects.filter(user=request.user).exists()
    context = {
        'user_profile': user_profile,
        'post': post,
        'form': form,
        'comments': comments,
        'following': following,
    }
    return render(request, 'post.html', context)


@login_required(login_url='/auth/login/')
@require_POST
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    if username != request.user.username:
        return redirect('index')
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if not form.is_valid():
        return render(request, 'new_post.html', {'form': form})
    form.save(commit=False)
    form.author = request.user
    form.text = form.cleaned_data['text']
    form.group = form.cleaned_data['group']
    form.save()
    return redirect('post', username=username, post_id=post_id)


@login_required(login_url='/auth/login/')
@require_http_methods(['GET', 'POST'])
def post_delete(request, username, post_id):
    post = Post.objects.get(id=post_id)
    if username != request.user.username:
        return redirect('index')
    if request.method == 'POST':
        post.delete()
        return redirect('profile', username=username)
    elif request.method == 'GET':
        return render(request, 'delete_post_confirm.html', {'post': post})


@login_required
@require_POST
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if not form.is_valid():
        context = {
            'form': form,
            'post': post,
        }
        return render(request, 'post.html', context)
    comment = form.save(commit=False)
    comment.post = post
    comment.author = request.user
    comment.text = form.cleaned_data['text']
    comment.save()
    return redirect('post', username=username, post_id=post_id)


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)
