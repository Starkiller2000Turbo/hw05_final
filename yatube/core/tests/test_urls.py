from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from mixer.backend.django import mixer

User = get_user_model()


class CoreURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = mixer.blend(User, username='auth')

        cls.auth = Client()

        cls.auth.force_login(cls.user)

    def test_404_httpstatus(self) -> None:
        """URL-адресы выдаёт https статусы ошибок"""
        response = Client().get('/test/missing_404')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_templates(self) -> None:
        """URL-адрес использует соответствующий шаблон."""
        response = Client().get('/test/missing_404')
        self.assertTemplateUsed(response, 'core/404.html')
