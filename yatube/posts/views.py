from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Post, Group, User
from .forms import PostForm


def index(request):
    post_list = Post.objects.order_by("-pub_date")
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "page": page,
        "paginator": paginator
    }
    return render(request, "index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by("-pub_date")[:12]
    context = {
        "group": group,
        "posts": posts
    }
    return render(request, "group.html", context)


def new_post(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect("index")

        form = PostForm()
        return render(request, "new_post.html", {"form": form})
    return redirect("login")


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user_profile.id).order_by("-pub_date")
    paginator = Paginator(posts, 5)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "user_profile": user_profile,
        "page": page,
        "paginator": paginator,
    }
    return render(request, "profile.html", context)


def post_view(request, username, post_id):
    user_profile = get_object_or_404(User, username=username)
    posts_count = Post.objects.filter(author=user_profile.id).count()
    post = get_object_or_404(Post, id=post_id)
    context = {
        "user_profile": user_profile,
        "post": post,
        "count": posts_count,
    }
    return render(request, "post.html", context)


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author == request.user:
        if request.method == "POST":
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                form.save(commit=False)
                form.author = request.user
                form.save()
                return redirect("index")
            return render(request, "new_post.html", {"form": form})

        form = PostForm(instance=post)
        return render(request, "new_post.html", {"form": form})
    return redirect("index")
