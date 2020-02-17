from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название группы")
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(verbose_name="Описание группы")

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name="Сообщение")
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User, verbose_name="Автор", on_delete=models.CASCADE,
                               related_name="author_posts")
    group = models.ForeignKey(Group, verbose_name="Группа", on_delete=models.SET_NULL,
                              blank=True, null=True, related_name="group_posts", )

    def __str__(self):
        return str(self.pk)
