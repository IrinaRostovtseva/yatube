from django.core import mail
from django.test import TestCase, Client
from django.urls import reverse

from .models import User, Post


class TestUserRegistration(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username="user", password="1234five")
        self.registration = self.client.post(
            "/auth/signup/", instance=self.user, follow=True)

    def test_reg_send_mail(self):
        if self.registration.status_code == 200:
            mail.send_mail("Вы зарегистрированы", "Регистрация прошла успешно",
                           "from@example.com", ["us@example.ru"])
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject, "Вы зарегистрированы")

    def test_user_profile(self):
        profile = self.client.get(
            reverse("profile", args=[self.user.username]))
        self.assertEqual(profile.status_code, 200)
        self.assertIn(
            profile.context["user_profile"].username, self.user.username)


class TestNewPost(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username="user", password="one2345")

    def test_auth_user(self):
        self.client.login(instance=self.user)
        response = self.client.get("/new/", follow=True)
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.client.logout()

    def test_not_auth_user(self):
        response = self.client.get("/new/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual("/auth/login/", response.redirect_chain[0][0])

    def test_post_creation(self):
        self.client.login(instance=self.user)
        post = Post.objects.create(author=self.user, text="Test text")
        response = self.client.post("/new/", instance=post, follow=True)
        self.assertEqual(response.status_code, 200)

        searched_content = f'<p class="post__text">{post.text}</p>'
        self.assertIn(searched_content, self.client.get("").content.decode())

        searched_content = f'<p class="user-posts__post-text">{post.text}</p>'
        response = self.client.get(reverse("profile", args=[post.author]))
        self.assertIn(searched_content, response.content.decode())

        response = self.client.get(
            reverse("post", args=[post.author, post.id]))
        self.assertIn(searched_content, response.content.decode())


class TestEditPost(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username="user", password="1234five")
        self.post = Post.objects.create(author=self.user, text="Test text")

    def test_not_auth_user(self):
        response = self.client.get(
            reverse("post_edit", args=[self.user.username, self.post.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual("/", response.redirect_chain[0][0])

    def test_post_editing(self):
        self.client.login(instance=self.user)
        response = self.client.get(
            reverse("post_edit", args=[self.user.username, self.post.id]), follow=True)
        self.assertEqual(response.status_code, 200)

        response_post = self.client.post(reverse("post_edit", args=[self.user.username, self.post.id]), {
                                         "author": self.post.author, "text": "I edit this text"}, follow=True)
        self.assertEqual(response_post.status_code, 200)

        searched_content = f'<p class="post__text">{self.post.text}</p>'
        self.assertIn(searched_content, self.client.get("").content.decode())

        searched_content = f'<p class="user-posts__post-text">{self.post.text}</p>'
        response = self.client.get(reverse("profile", args=[self.post.author]))
        self.assertIn(searched_content, response.content.decode())

        response = self.client.get(
            reverse("post", args=[self.post.author, self.post.id]))
        self.assertIn(searched_content, response.content.decode())

    def tearDown(self):
        self.client.logout()


class TestDeletePost(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username="user", password="1234five")
        self.post = Post.objects.create(author=self.user, text="Test text")

    def test_not_auth_user(self):
        response = self.client.get(
            reverse("post_delete", args=[self.user.username, self.post.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual("/", response.redirect_chain[0][0])

    def test_post_delete(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("post_delete", args=[self.user.username, self.post.id]), data=None, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            reverse("profile", args=[self.user.username]), response.redirect_chain[0][0])

        searched_content = f'<p class="post__text">{self.post.text}</p>'
        self.assertNotIn(searched_content,
                         self.client.get("").content.decode())

        searched_content = f'<p class="user-posts__post-text">{self.post.text}</p>'
        response = self.client.get(reverse("profile", args=[self.post.author]))
        self.assertNotIn(searched_content, response.content.decode())

        response = self.client.get(
            reverse("post", args=[self.post.author, self.post.id]))
        self.assertEqual(response.status_code, 404)

    def tearDown(self):
        self.client.logout()
