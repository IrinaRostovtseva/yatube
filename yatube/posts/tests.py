import os

from django.conf import settings
from django.core import mail
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from .models import Group, Post, User


class TestUserRegistration(TestCase):
    def setUp(self):
        self.client = Client()
        self.registration = self.client.post(
            reverse("signup"), {"username": "user", "password1": "A2345678", "password2": "A2345678", "email": "us@example.ru", "first_name": "user", "last_name": "user"}, follow=True)

    def test_reg_send_mail(self):
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Регистрации на Yatube")

    def test_user_profile(self):
        profile = self.client.get(
            reverse("profile", args=["user"]))
        self.assertEqual(profile.status_code, 200)
        self.assertIn(
            profile.context["user_profile"].username, "user")


class TestNewPost(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username="user", password="one2345")

    def test_auth_user(self):
        self.client.login(instance=self.user)
        response = self.client.get(reverse("new_post"), follow=True)
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.client.logout()

    def test_not_auth_user(self):
        response = self.client.get(reverse("new_post"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(reverse("login"), response.redirect_chain[0][0])

    def test_post_creation(self):
        self.client.force_login(self.user)
        cache.clear()
        post = Post.objects.create(author=self.user, text="Test text")
        response = self.client.post(
            reverse("new_post"), instance=post, follow=True)
        self.assertEqual(response.status_code, 200)

        searched_content = f'<p class="post__text">{post.text}</p>'
        self.assertIn(searched_content, self.client.get(
            reverse("index")).content.decode())

        searched_content = f'<p class="post__text">{post.text}</p>'
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
        self.assertEqual(reverse("index"), response.redirect_chain[0][0])

    def test_post_editing(self):
        self.client.login(instance=self.user)
        cache.clear()
        response = self.client.get(
            reverse("post_edit", args=[self.user.username, self.post.id]), follow=True)
        self.assertEqual(response.status_code, 200)

        response_post = self.client.post(reverse("post_edit", args=[self.user.username, self.post.id]), {
                                         "author": self.post.author, "text": "I edit this text"}, follow=True)
        self.assertEqual(response_post.status_code, 200)

        searched_content = f'<p class="post__text">{self.post.text}</p>'
        self.assertIn(searched_content, self.client.get("").content.decode())

        searched_content = f'<p class="post__text">{self.post.text}</p>'
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
        self.assertEqual(reverse("index"), response.redirect_chain[0][0])

    def test_post_delete(self):
        self.client.force_login(self.user)
        cache.clear()
        response = self.client.post(
            reverse("post_delete", args=[self.user.username, self.post.id]), data=None, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            reverse("profile", args=[self.user.username]), response.redirect_chain[0][0])

        searched_content = f'<p class="post__text">{self.post.text}</p>'
        self.assertNotIn(searched_content,
                         self.client.get("").content.decode())

        searched_content = f'<p class="post__text">{self.post.text}</p>'
        response = self.client.get(reverse("profile", args=[self.post.author]))
        self.assertNotIn(searched_content, response.content.decode())

        response = self.client.get(
            reverse("post", args=[self.post.author, self.post.id]))
        self.assertEqual(response.status_code, 404)

    def tearDown(self):
        self.client.logout()


class TestPageNotFound(TestCase):
    def setUp(self):
        self.client = Client()

    def test_page_not_found_code(self):
        response = self.client.get("/oops/")
        self.assertEqual(response.status_code, 404)


class TestImageUpload(TestCase):
    def setUp(self):
        self.client = Client()
        cache.clear()
        self.user = User.objects.create(username="user", password="one2345")
        self.client.force_login(self.user)
        self.group = Group.objects.create(
            title="cactuars", slug="cact", description="all about cactuars")

    def test_image_being(self):
        with open(os.path.join(settings.BASE_DIR, "test_pic.jpg"), "rb") as fp:
            self.client.post(
                reverse("new_post"), {"text": "post with pic", "group": self.group.id, "image": fp}, follow=True)

            response = self.client.get("/user/1/")
            self.assertIn("<img", response.content.decode())
            self.assertIn("<img", self.client.get(
                reverse("index")).content.decode())

            response = self.client.get(
                reverse("profile", args=[self.user.username]))
            self.assertIn("<img", response.content.decode())
            response = self.client.get(
                reverse("group", args=[self.group.slug]))
            self.assertIn('<img', response.content.decode())

    def tearDown(self):
        cache.clear()

    def test_not_image_upload(self):
        with open(os.path.join(settings.BASE_DIR, "requirements.txt"), "rb") as fp:
            response = self.client.post(
                reverse("new_post"), {"text": "post with non pic", "image": fp})
            self.assertNotIn("<img", self.client.get(
                "/user/1/").content.decode())


class TestIndexPageCache(TestCase):
    def setUp(self):
        self.client = Client()
        cache.clear()
        self.user = User.objects.create(username="user", password="1234five")
        self.client.force_login(self.user)

    def test_index_cache(self):
        post1 = Post.objects.create(author=self.user, text="Test post 1")
        response = self.client.get(reverse("index"))
        self.assertIn("Test post 1", self.client.get(
            reverse("index")).content.decode())
        post2 = Post.objects.create(author=self.user, text="Test post 2 ")
        self.assertNotIn("Test post 2", self.client.get(
            reverse("index")).content.decode())
        cache.clear()
        self.assertIn("Test post 2", self.client.get(
            reverse("index")).content.decode())


class TestComment(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username="user", password="12345678")
        self.post = Post.objects.create(
            author=self.user, text="Test post for comments")

    def test_not_auth_comment(self):
        response = self.client.post(reverse("add_comment", args=[self.user.username, self.post.id]), {
                                    "post": self.post, "text": "I am not logged in, but I wanna comment"}, follow=True)
        self.assertEqual(reverse("login"), response.redirect_chain[0][0])

    def test_auth_comment(self):
        self.client.force_login(self.user)
        add_comment = self.client.post(reverse("add_comment", args=[self.user.username, self.post.id]), {
                                       "post": self.post, "author": self.user, "text": "Hey, I am logged in. Cool post"}, follow=True)
        response = self.client.get(
            reverse("post", args=[self.user.username, self.post.id]))
        self.assertIn("Hey, I am logged in. Cool post",
                      response.content.decode())


class TestFollow(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create(username="cact", password="12345678")
        self.user2 = User.objects.create(username="desert", password="abcdefg")
        self.client.force_login(self.user1)

    def test_auth_follow(self):
        response_follow = self.client.get(
            reverse("profile_follow", args=[self.user2.username]), follow=True)
        self.assertEqual(response_follow.status_code, 200)
        response = self.client.get(
            reverse("profile", args=[self.user1.username]))
        self.assertContains(
            response, "<td>Подписан:</td>\n<td>1</td>", html=True)

    def test_auth_unfollow(self):
        response_follow = self.client.get(
            reverse("profile_follow", args=[self.user2.username]), follow=True)
        response_unfollow = self.client.get(
            reverse("profile_unfollow", args=[self.user2.username]), follow=True)
        self.assertEqual(response_unfollow.status_code, 200)

        response = self.client.get(
            reverse("profile", args=[self.user1.username]))
        self.assertContains(
            response, "<td>Подписан:</td>\n<td>0</td>", html=True)

    def test_following_post(self):
        response_follow = self.client.get(
            reverse("profile_follow", args=[self.user2.username]), follow=True)
        post1 = Post.objects.create(
            author=self.user1, text="You\'re not following me")
        post2 = Post.objects.create(author=self.user2, text="Hello user1")

        # favourite posts for user1
        response1 = self.client.get(reverse("follow_index"))
        self.assertContains(response1, post2.text, html=True)

        # favourite posts for user2
        self.client.logout()
        self.client.force_login(self.user2)
        response1 = self.client.get(reverse("follow_index"))
        self.assertNotContains(response1, post1.text, html=True)

    def test_not_auth_follow(self):
        self.client.logout()
        response = self.client.get(
            reverse("profile_follow", args=[self.user2.username]), follow=True)
        self.assertEqual(reverse("login"), response.redirect_chain[0][0])
