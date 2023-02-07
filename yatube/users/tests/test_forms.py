from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from users.forms import CreationForm

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.form = CreationForm()

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_user(self) -> None:
        """Валидная форма создает нового пользователя."""
        user_count = User.objects.count()
        form_data = {
            'first_name': 'Тестовое имя',
            'last_name': 'Тестовая фамилия',
            'username': 'test_username',
            'email': 'test_email@mail.ru',
            'password1': 'test_password',
            'password2': 'test_password',
        }
        response = self.authorized_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), user_count + 1)
        self.assertTrue(
            User.objects.filter(
                first_name='Тестовое имя',
                last_name='Тестовая фамилия',
                username='test_username',
                email='test_email@mail.ru',
            ).exists(),
        )
