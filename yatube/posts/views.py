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
    posts = Post.objects.filter(group=group).order_by("-pub_date")
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
                form.text = form.cleaned_data["text"]
                form.group = form.cleaned_data["group"]
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
    if username == str(request.user):
        if request.method == "POST":
            form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
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


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
