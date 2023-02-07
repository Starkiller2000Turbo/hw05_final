from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            pk=1,
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            pk=2,
            author=self.user,
            text='Тестовый пост',
        )

    def test_urls_use_correct_templates(self) -> None:
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/auth/login/': 'registration/login.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/logout/': 'registration/logged_out.html',
            '/auth/passwords/reset/': 'registration/password_reset_form.html',
            '/auth/passwords/reset/complete/': (
                'registration/password_reset_complete.html'
            ),
            '/auth/passwords/reset/done/': (
                'registration/password_reset_done.html'
            ),
            '/auth/reset/Mw/680-8a133dac86b01bc7dda2/': (
                'registration/password_reset_confirm.html'
            ),
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_authorized_urls_use_correct_templates(self) -> None:
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/auth/passwords/change/': (
                'registration/password_change_form.html'
            ),
            '/auth/passwords/change/done/': (
                'registration/password_change_done.html'
            ),
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_non_authorized_urls_exist_at_desired_location(self) -> None:
        """Тестирование страниц на отсутствие авторизации"""
        pages = {
            '/auth/passwords/change/': (
                '/auth/login/?next=/auth/passwords/change/'
            ),
            '/auth/passwords/change/done/': (
                '/auth/login/?next=/auth/passwords/change/done/'
            ),
        }
        for page, redirect_page in pages.items():
            with self.subTest(page=page):
                response = self.guest_client.get(page, follow=True)
                self.assertRedirects(response, redirect_page)
