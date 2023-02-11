from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user_author, cls.user = mixer.cycle(2).blend(
            User,
            username=(
                name
                for name in (
                    'author',
                    'auth',
                )
            ),
        )
        cls.group = mixer.blend(Group)
        cls.post = mixer.blend(Post, author=cls.user_author, group=cls.group)

        cls.auth = Client()
        cls.author = Client()

        cls.auth.force_login(cls.user)
        cls.author.force_login(cls.user_author)

        cls.urls = {
            'create': reverse('posts:post_create'),
            'edit': reverse(
                'posts:post_edit',
                args=(cls.post.pk,),
            ),
            'group': reverse(
                'posts:group_list',
                args=(cls.group.slug,),
            ),
            'index': reverse('posts:index'),
            'post': reverse(
                'posts:post_detail',
                args=(cls.post.pk,),
            ),
            'profile': reverse(
                'posts:profile',
                args=(cls.user_author.username,),
            ),
            'comment': reverse(
                'posts:add_comment',
                args=(cls.post.pk,),
            ),
            'follow': reverse('posts:follow_index'),
            'missing': '/test/missing_url',
        }

    def setUp(self) -> None:
        cache.clear()

    def test_httpstatuses(self) -> None:
        """URL-адрес существует и выдаёт https статус 200."""
        httpstatuses = (
            (self.urls.get('group'), HTTPStatus.OK, self.client),
            (self.urls.get('index'), HTTPStatus.OK, self.client),
            (self.urls.get('post'), HTTPStatus.OK, self.client),
            (self.urls.get('profile'), HTTPStatus.OK, self.client),
            (self.urls.get('create'), HTTPStatus.FOUND, self.client),
            (self.urls.get('create'), HTTPStatus.OK, self.auth),
            (self.urls.get('edit'), HTTPStatus.FOUND, self.client),
            (self.urls.get('edit'), HTTPStatus.FOUND, self.auth),
            (self.urls.get('edit'), HTTPStatus.OK, self.author),
            (self.urls.get('comment'), HTTPStatus.FOUND, self.auth),
            (self.urls.get('follow'), HTTPStatus.FOUND, self.client),
            (self.urls.get('follow'), HTTPStatus.OK, self.auth),
            (self.urls.get('missing'), HTTPStatus.NOT_FOUND, self.client),
        )
        for address, code, client in httpstatuses:
            with self.subTest(
                address=address,
                code=code,
                client=client,
            ):
                self.assertEqual(client.get(address).status_code, code)

    def test_templates(self) -> None:
        """URL-адрес использует соответствующий шаблон."""
        templates = (
            (self.urls.get('group'), 'posts/group_list.html', self.client),
            (self.urls.get('index'), 'posts/index.html', self.client),
            (self.urls.get('post'), 'posts/post_detail.html', self.client),
            (self.urls.get('profile'), 'posts/profile.html', self.client),
            (self.urls.get('create'), 'posts/create_post.html', self.auth),
            (self.urls.get('edit'), 'posts/create_post.html', self.author),
            (self.urls.get('follow'), 'posts/follow.html', self.auth),
        )
        for address, template, client in templates:
            with self.subTest(
                address=address,
                template=template,
                client=client,
            ):
                self.assertTemplateUsed(client.get(address), template)

    def test_redirects(self) -> None:
        """Тестирование страниц на отсутствие авторизации."""
        pages = (
            (
                self.urls.get('create'),
                redirect_to_login(self.urls.get('create')).url,
                self.client,
            ),
            (
                self.urls.get('edit'),
                redirect_to_login(self.urls.get('edit')).url,
                self.client,
            ),
            (
                self.urls.get('comment'),
                redirect_to_login(self.urls.get('comment')).url,
                self.client,
            ),
            (
                self.urls.get('follow'),
                redirect_to_login(self.urls.get('follow')).url,
                self.client,
            ),
            (
                self.urls.get('edit'),
                self.urls.get('post'),
                self.auth,
            ),
        )
        for page, redirect_page, client in pages:
            with self.subTest(
                page=page,
                redirect_page=redirect_page,
                client=client,
            ):
                self.assertRedirects(
                    client.get(page, follow=True),
                    redirect_page,
                )
