#from django.shortcuts import render
from django.http import HttpResponse
from .models import Post
# Create your views here.

def index(request):
    latest = Post.objects.order_by("-pub_date")[:10]
    output = []
    for item in latest:
        output.append(item.text)
    return HttpResponse("/n".join(output))
