from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class AboutURLTests(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()

    def test_verbose_name(self) -> None:
        """Тестирование общедоступных страниц"""
        pages = ['/about/author/', '/about/tech/']
        for page in pages:
            with self.subTest(field=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, 200)


class AboutPagesTests(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()

    def test_pages_use_correct_templates(self) -> None:
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
