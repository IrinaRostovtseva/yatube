from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название группы")
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(verbose_name="Описание группы")

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name="Сообщение")
    pub_date = models.DateTimeField(
        "date published", auto_now_add=True, db_index=True)
    author = models.ForeignKey(User, verbose_name="Автор", on_delete=models.CASCADE,
                               related_name="author_posts")
    group = models.ForeignKey(Group, verbose_name="Группа", on_delete=models.SET_NULL,
                              blank=True, null=True, related_name="group_posts", )
    image = models.ImageField(upload_to="posts/",
                              null=True, blank=True, verbose_name="Изображение")

    def __str__(self):
        return str(self.pk)


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments_post")
    author = models.ForeignKey(
        User, verbose_name="Автор", on_delete=models.CASCADE, related_name="comment_author")
    text = models.TextField(verbose_name="Комментарий")
    created = models.DateTimeField("date published", auto_now_add=True)

    def __str__(self):
        return str(self.pk)


class Follow(models.Model):
    # ссылка на объект пользователя, который подписывается
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower")
    # ссылка на объект пользователя, на которого подписываются
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following", blank=True, null=True)

    class Meta:
        unique_together = ["user", "author"]

    def __str__(self):
        return f"{self.user} -> {self.author}"
