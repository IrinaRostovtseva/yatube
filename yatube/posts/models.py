from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class Post(models.Model):
    text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
# Create your models here.
