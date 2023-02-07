from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_authorized_pages_use_correct_templates(self) -> None:
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse(
                'users:pass_change',
            ): 'registration/password_change_form.html',
            reverse(
                'users:pass_change_done',
            ): 'registration/password_change_done.html',
            reverse(
                'users:pass_reset_done',
            ): 'registration/password_reset_done.html',
            reverse(
                'users:pass_reset_complete',
            ): 'registration/password_reset_complete.html',
            reverse(
                'users:pass_reset',
            ): 'registration/password_reset_form.html',
            reverse(
                'users:pass_reset_confirm',
                kwargs={'uidb64': 'Mv', 'token': '680-8a133dac86b01bc7dda2'},
            ): 'registration/password_reset_confirm.html',
            reverse('users:login'): 'registration/login.html',
            reverse('users:logout'): 'registration/logged_out.html',
            reverse('users:signup'): 'users/signup.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_signup_shows_correct_context(self) -> None:
        """Шаблон signup.html сформирован с правильным контекстом."""
        page = reverse('users:signup')
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.CharField,
        }
        with self.subTest(page=page):
            response = self.authorized_client.get(page)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)
