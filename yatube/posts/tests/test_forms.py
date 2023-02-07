import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Comment, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = mixer.blend(User, username='auth')

        cls.auth = Client()

        cls.auth.force_login(cls.user)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self) -> None:
        """Валидная форма создает ноый пост."""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        group = mixer.blend(Group)
        form_data = {
            'text': 'Тестовый текст',
            'group': group.id,
            'image': uploaded,
        }
        response = self.auth.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': 'auth'},
            ),
        )
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.get()
        self.assertEqual(post.text, 'Тестовый текст')
        self.assertEqual(post.group, group)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.image.name, 'posts/small.gif')

    def test_edit_post(self) -> None:
        """Валидная форма редактирует пост."""
        user_author = mixer.blend(User, username='author')
        author = Client()
        author.force_login(user_author)
        group1, group2 = mixer.cycle(2).blend(Group)
        post = mixer.blend(Post, author=user_author, group=group1)
        small1_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small1.gif',
            content=small1_gif,
            content_type='image/gif',
        )
        form_data = {
            'text': 'Изменённый тестовый текст',
            'group': group2.id,
            'image': uploaded,
        }
        response = author.post(
            reverse('posts:post_edit', kwargs={'pk': post.pk}),
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
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.get()
        self.assertEqual(post.text, 'Изменённый тестовый текст')
        self.assertEqual(post.group, group2)
        self.assertEqual(post.author, user_author)
        self.assertEqual(post.image.name, 'posts/small1.gif')

    def test_anonymous_user_can_not_create(self) -> None:
        """Анонимный пользователь не может создать пост."""
        form_data = {
            'text': 'Тестовый текст',
        }
        Client().post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 0)

    def test_anonymous_user_can_not_edit(self) -> None:
        """Анонимный пользователь не может изменить пост."""
        user_author = mixer.blend(User, username='author')
        author = Client()
        author.force_login(user_author)
        post = mixer.blend(Post, text='Тестовый текст', author=user_author)
        form_data = {
            'text': 'Изменённый тестовый текст',
        }
        Client().post(
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
        user_author = mixer.blend(User, username='author')
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
        cls.user = mixer.blend(User, username='auth')

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
        Client().post(
            reverse(
                'posts:add_comment',
                kwargs={'pk': post.pk},
            ),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), 0)
