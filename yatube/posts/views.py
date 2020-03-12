from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Group, Post, User, Follow


def index(request):
    post_list = Post.objects.select_related("author").order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "page": page,
        "paginator": paginator
    }
    return render(request, "index.html", context)


def follow_index(request):
    if request.user.is_authenticated:
        post_list = Post.objects.select_related("author").filter(
            author__following__user=request.user).order_by("-pub_date")
        paginator = Paginator(post_list, 10)
        page_number = request.GET.get("page")
        page = paginator.get_page(page_number)
        context = {
            "page": page,
            "paginator": paginator
        }
        return render(request, "index.html", context)
    return redirect("login")


def profile_follow(request, username):
    if request.user.is_authenticated:
        if request.user.username == username:
            return redirect("profile", username=username)

        following = User.objects.get(username=username)
        is_follow = Follow.objects.filter(
            user=request.user, author=following).exists()
        if request.method == "GET":
            if is_follow:
                return redirect("profile_unfollow", username=username)
            Follow.objects.create(user=request.user, author=following)
            return redirect("profile", username=username)
    return redirect("login")


def profile_unfollow(request, username):
    if request.user.is_authenticated:
        following = get_object_or_404(User, username=username)
        if request.method == "GET":
            follow = Follow.objects.filter(
                user=request.user.id, author=following).delete()
            return redirect("profile", username=username)
    return redirect("login")


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.select_related("author", "group").filter(
        group=group).order_by("-pub_date")
    paginator = Paginator(posts, 10)
    page_num = request.GET.get("page")
    page = paginator.get_page(page_num)
    context = {
        "group": group,
        "paginator": paginator,
        "page": page
    }
    return render(request, "group.html", context)


def new_post(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = PostForm(request.POST or None, files=request.FILES or None)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.text = form.cleaned_data["text"]
                post.group = form.cleaned_data["group"]
                post.save()
                return redirect("index")

        form = PostForm()
        return render(request, "new_post.html", {"form": form})
    return redirect("login")


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    posts = Post.objects.select_related("author").filter(
        author=user_profile.id).order_by("-pub_date")
    posts_count = posts.count()
    paginator = Paginator(posts, 5)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    following = False
    follower_count = Follow.objects.select_related(
        "author").filter(user=user_profile).count()
    following_count = Follow.objects.select_related(
        "user").filter(author=user_profile).count()
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=user_profile).exists()
    context = {
        "user_profile": user_profile,
        "page": page,
        "paginator": paginator,
        "following": following,
        "following_count": following_count,
        "follower_count": follower_count,
        "posts_count": posts_count,
    }
    return render(request, "profile.html", context)


def post_view(request, username, post_id):
    user_profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    posts_count = Post.objects.filter(author=user_profile).count()
    form = CommentForm()
    comments = Comment.objects.select_related("post", "author").filter(post=post_id).order_by("-created")
    comments_count = comments.count()
    following = False
    follower_count = Follow.objects.select_related(
        "author").filter(user=user_profile).count()
    following_count = Follow.objects.select_related(
        "user").filter(author=user_profile).count()
    if request.user.is_authenticated:
        Follow.objects.filter(user=request.user, author=user_profile).exists()
    context = {
        "user_profile": user_profile,
        "post": post,
        "form": form,
        "comments": comments,
        "following": following,
        "following_count": following_count,
        "follower_count": follower_count,
        "posts_count": posts_count,
        "comments_count": comments_count,
    }
    return render(request, "post.html", context)


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    if username == request.user.username:
        if request.method == "POST":
            form = PostForm(request.POST or None,
                            files=request.FILES or None, instance=post)
            if form.is_valid():
                form.save(commit=False)
                form.author = request.user
                form.text = form.cleaned_data["text"]
                form.group = form.cleaned_data["group"]
                form.save()
                return redirect("post", username=username, post_id=post_id)
            context = {
                "form": form,
                "post": post
            }
            return render(request, "new_post.html", context)

        form = PostForm(instance=post)
        context = {
            "form": form,
            "post": post
        }
        return render(request, "new_post.html", context)
    return redirect("index")


def post_delete(request, username, post_id):
    post = Post.objects.get(id=post_id)
    if username == str(request.user):
        if request.method == "POST":
            post.delete()
            return redirect("profile", username=username)
        return render(request, "delete_post_confirm.html", {"post": post})
    return redirect("index")


def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user.is_authenticated:
        if request.method == "POST":
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.text = form.cleaned_data["text"]
                comment.save()
                return redirect("post", username=username, post_id=post_id)

            context = {
                "form": form,
                "post": post,
            }
            return render(request, "post.html", context)
        return redirect("post", username=username, post_id=post_id)
    return redirect("login")


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
