from django.shortcuts import render, get_object_or_404
from .models import Post, Group


def index(request):
    latest = Post.objects.order_by("-pub_date")[:11]
    context = {
        "posts": latest,
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
