import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Comment, Follow, Group, Post
from posts.tests.common import image

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = mixer.blend(User)

        cls.auth = Client()

        cls.auth.force_login(cls.user)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self) -> None:
        """Валидная форма создает ноый пост."""
        group = mixer.blend(Group)
        data = {
            'text': 'Тестовый текст',
            'group': group.id,
            'image': image(name='test.png'),
        }
        response = self.auth.post(
            reverse('posts:post_create'),
            data=data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.get_username()},
            ),
        )
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.get()
        self.assertEqual(post.text, 'Тестовый текст')
        self.assertEqual(post.group, group)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.image.name, 'posts/test.png')

    def test_edit_post(self) -> None:
        """Валидная форма редактирует пост."""
        user_author = mixer.blend(User, username='author')
        group1, group2 = mixer.cycle(2).blend(Group)
        post = mixer.blend(Post, author=user_author, group=group1)

        author = Client()

        author.force_login(user_author)

        data = {
            'text': 'Изменённый тестовый текст',
            'group': group2.id,
            'image': image(name='test1.png'),
        }
        response = author.post(
            reverse('posts:post_edit', kwargs={'pk': post.pk}),
            data=data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'pk': post.pk},
            ),
        )
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.get()
        self.assertEqual(post.text, 'Изменённый тестовый текст')
        self.assertEqual(post.group, group2)
        self.assertEqual(post.author, user_author)
        self.assertEqual(post.image.name, 'posts/test1.png')

    def test_anonymous_user_can_not_create(self) -> None:
        """Анонимный пользователь не может создать пост."""
        form_data = {
            'text': 'Тестовый текст',
        }
        self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 0)

    def test_anonymous_user_can_not_edit(self) -> None:
        """Анонимный пользователь не может изменить пост."""
        user_author = mixer.blend(User)
        author = Client()
        author.force_login(user_author)
        post = mixer.blend(Post, text='Тестовый текст', author=user_author)
        form_data = {
            'text': 'Изменённый тестовый текст',
        }
        self.client.post(
            reverse('posts:post_edit', kwargs={'pk': post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.get()
        self.assertEqual(post.text, 'Тестовый текст')
        self.assertEqual(post.author, user_author)

    def test_not_author_can_not_edit(self) -> None:
        """Не автор не может изменить пост."""
        user_author = mixer.blend(User)
        author = Client()
        author.force_login(user_author)
        post = mixer.blend(Post, text='Тестовый текст', author=user_author)
        form_data = {
            'text': 'Изменённый тестовый текст',
        }
        self.auth.post(  #
            reverse('posts:post_edit', kwargs={'pk': post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.get()
        self.assertEqual(post.text, 'Тестовый текст')
        self.assertEqual(post.author, user_author)


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = mixer.blend(User)

        cls.auth = Client()

        cls.auth.force_login(cls.user)

    def test_add_comment(self) -> None:
        """Валидная форма создает ноый пост."""
        post = mixer.blend(Post)
        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.auth.post(
            reverse(
                'posts:add_comment',
                kwargs={'pk': post.pk},
            ),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'pk': post.pk},
            ),
        )
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.get(post=post)
        self.assertEqual(comment.text, 'Тестовый текст')
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, post)

    def test_anonymous_user_can_not_add_comment(self) -> None:
        """Анонимный пользователь не может создать пост."""
        post = mixer.blend(Post)
        form_data = {
            'text': 'Тестовый текст',
        }
        self.client.post(
            reverse(
                'posts:add_comment',
                kwargs={'pk': post.pk},
            ),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), 0)


class FollowFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_auth, cls.user_author = mixer.cycle(2).blend(User)

        cls.auth = Client()
        cls.author = Client()

        cls.auth.force_login(cls.user_auth)
        cls.author.force_login(cls.user_author)

    def test_add_following(self) -> None:
        """Запрос создаёт новую подписку."""
        response = self.auth.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_author.get_username()},
            ),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user_author.get_username()},
            ),
        )
        self.assertEqual(Follow.objects.count(), 1)
        following = Follow.objects.get()
        self.assertEqual(following.author, self.user_author)
        self.assertEqual(following.user, self.user_auth)
