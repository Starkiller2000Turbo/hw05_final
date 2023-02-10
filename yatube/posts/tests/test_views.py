from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models
from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Comment, Follow, Group, Post
from yatube import settings

User = get_user_model()


def check_types_in_dict(self, model: Group or Post, fields: dict) -> None:
    for value, expected in fields.items():
        with self.subTest(value=value):
            form_field = model._meta.get_field(value)
            self.assertIsInstance(form_field, expected)


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def setUp(self) -> None:
        cache.clear()
        self.user = User.objects.create_user(username='auth')
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        self.post = Post.objects.create(
            id=2,
            author=self.user,
            text='Тестовый пост',
            group=self.group,
        )

        self.authorized_client = Client()

        self.authorized_client.force_login(self.user)

    def test_pages_show_correct_context(self) -> None:
        """Шаблоны страниц сформированы с правильным контекстом."""
        page_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'}),
            reverse('posts:post_detail', kwargs={'pk': '2'}),
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'pk': '2'}),
        ]
        post_fields = {
            'text': models.TextField,
            'created': models.DateTimeField,
            'image': models.ImageField,
        }
        group_fields = {
            'slug': models.SlugField,
            'description': models.TextField,
            'title': models.CharField,
        }
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
            'image': forms.ImageField,
        }
        for page in page_names:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                if response.context.get('post'):
                    check_types_in_dict(
                        self,
                        response.context.get('post'),
                        post_fields,
                    )
                    check_types_in_dict(
                        self,
                        response.context.get('post').group,
                        group_fields,
                    )
                elif response.context.get('page_obj'):
                    for post in response.context.get('page_obj'):
                        check_types_in_dict(self, post, post_fields)
                        check_types_in_dict(
                            self,
                            post.group,
                            group_fields,
                        )
                elif response.context.get('form'):
                    for value, expected in form_fields.items():
                        with self.subTest(value=value):
                            form_field = response.context.get(
                                'form',
                            ).fields.get(value)
                            self.assertIsInstance(form_field, expected)

    def test_post_shows_up_on_pages(self) -> None:
        page_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'}),
        ]
        for page in page_names:
            response = self.client.get(page)
            self.assertEqual(
                response.context['page_obj'][0].text,
                'Тестовый пост',
            )


class CommentPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='auth')
        self.post = mixer.blend(
            Post,
            author=self.user,
        )
        self.comment = mixer.blend(
            Comment,
            post=self.post,
            author=self.user,
            text='Тестовый текст',
        )

        self.authorized_client = Client()

        self.authorized_client.force_login(self.user)

    def test_comment_shows_up_on_post_page(self) -> None:
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                args=(self.post.pk,),
            ),
        )
        self.assertEqual(
            response.context['post'].comments.all()[0].text,
            'Тестовый текст',
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def setUp(self) -> None:
        cache.clear()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        for pk in range(13):
            self.post = Post.objects.create(
                id=pk,
                author=self.user,
                text=f'Тестовый пост №{pk}',
                group=self.group,
            )

    def test_first_page_contains_value_of_records(self) -> None:
        page_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'}),
        ]
        for page in page_names:
            response = self.client.get(page)
            self.assertEqual(
                len(response.context['page_obj']),
                settings.OBJECTS_ON_PAGE,
            )

    def test_second_page_contains_value_of_records(self) -> None:
        page_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'}),
        ]
        for page in page_names:
            response = self.client.get(page + '?page=2')
            self.assertEqual(
                len(response.context['page_obj']),
                13 - settings.OBJECTS_ON_PAGE,
            )


class FollowPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.subscribed, cls.author, cls.non_subscribed = mixer.cycle(3).blend(
            User,
        )
        cls.post = mixer.blend(Post, author=cls.author, text='Тестовый пост')
        cls.following = Follow.objects.create(
            user=cls.subscribed,
            author=cls.author,
        )

        cls.subscribed_client = Client()
        cls.non_subscribed_client = Client()

        cls.subscribed_client.force_login(cls.subscribed)
        cls.non_subscribed_client.force_login(cls.non_subscribed)

    def setUp(self) -> None:
        cache.clear()

    def test_post_shows_up_only_for_subscribed_user(self) -> None:
        """Пост появляется только на странице подписанного пользователя."""
        response = self.subscribed_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            response.context['page_obj'][0].text,
            'Тестовый пост',
        )
        response = self.non_subscribed_client.get(
            reverse('posts:follow_index'),
        )
        self.assertEqual(
            len(response.context['page_obj']),
            0,
        )

    def test_user_can_regulate_followings(self) -> None:
        """пользователь может подписываться и удалять из подписок."""
        self.non_subscribed_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author.username},
            ),
        )
        self.assertEqual(
            Follow.objects.filter(user=self.non_subscribed).count(),
            1,
        )
        self.non_subscribed_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author.username},
            ),
        )
        self.assertEqual(
            Follow.objects.filter(user=self.non_subscribed).count(),
            0,
        )
